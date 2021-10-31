import logging
import time
from threading import Thread, Event

from django.conf import settings
# noinspection PyPackageRequirements
from telegram import Update, Message
# noinspection PyPackageRequirements
from telegram.utils.helpers import from_timestamp
# noinspection PyPackageRequirements
from telegram.utils.types import JSONDict

from moonrobot.core.notion.notion_client import create_notion_page
from moonrobot.core.notion.notion_rich_text import rich_text_from_telegram_entities
from moonrobot.core.utils import construct_unique_msg_id
from moonrobot.models import MrbMessage, MrbUserMessage, MrbBotMessage

logger = logging.getLogger(__name__)

notion_db_sync_event = Event()


def _sync_db_to_notion_continuously():
    while True:
        notion_db_sync_event.wait()
        notion_db_sync_event.clear()  # TODO oleksandr: this is terrible =\ use some sort of a lock to do this ?

        # TODO oleksandr: guard with try/except
        _sync_db_to_notion()  # TODO oleksandr: sync only one object, not all at once (no loops inside)
        time.sleep(1)  # TODO oleksandr: make it configurable ?


_notion_sync_thread = Thread(
    name='_notion_sync_thread',
    target=_sync_db_to_notion_continuously,
    daemon=True,  # TODO oleksandr: is daemon=True a bad idea ?
)
_notion_sync_thread.start()  # TODO oleksandr: use a pool of workers ?


# TODO oleksandr: think what kind of racing conditions are possible (decide on transaction isolation mechanism)
# TODO oleksandr: use transaction.atomic ?
def _sync_db_to_notion() -> None:
    from moonrobot.core.telegram_bot import get_bot

    messages = MrbMessage.objects.filter(notion_synced=False, notion_sync_failed=False).order_by('sent_timestamp')
    for message in messages:  # TODO oleksandr: get rid of this loop - only one item per second or so ! :(
        # noinspection PyBroadException
        try:
            if message.from_user:
                user_message = MrbUserMessage.objects.get(id=message.id)
                t_update = Update.de_json(user_message.update_payload, get_bot())
                t_message = t_update.effective_message
            else:
                bot_message = MrbBotMessage.objects.get(id=message.id)
                t_message = Message.de_json(bot_message.response_payload, get_bot())

            latest_chat_messages = MrbMessage.objects.filter(chat_id=t_message.chat_id).order_by('-sent_timestamp')[:2]
            prev_message = None
            for prev_message in latest_chat_messages:
                if prev_message != message:
                    break

            reply_to_msg = None
            if t_message.reply_to_message:
                reply_to_unique = construct_unique_msg_id(t_message.reply_to_message)
                reply_to_msg = MrbMessage.objects.filter(unique_msg_id=reply_to_unique).first()

            sent_zulu_time = from_timestamp(message.sent_timestamp)
            if sent_zulu_time:
                sent_zulu_time = sent_zulu_time.isoformat(sep=' ', timespec='seconds').replace('+00:00', 'Z')
            else:
                sent_zulu_time = ''

            notion_create_request = {
                'parent': {  # TODO oleksandr: move this inside of notion_client.py
                    'database_id': settings.MRB_NOTION_MESSAGES_DB_ID,
                },
                'properties': {
                    'From': {
                        'title': [
                            {
                                'text': {
                                    'content': message.user_display_name if message.from_user else 'BOT',
                                },
                            },
                        ],
                    },
                    'From user': {
                        'checkbox': message.from_user,
                    },
                    'Message': {
                        'rich_text': rich_text_from_telegram_entities(
                            message.plain_text or '',
                            message.text_entities or [],
                        ),
                    },
                    'Timestamp': {
                        'rich_text': [
                            {
                                'text': {
                                    'content': sent_zulu_time,
                                },
                            },
                        ],
                    },
                },
            }
            if message.from_user:
                notion_create_request['properties']['Username'] = _build_username(message)
            if prev_message and prev_message.notion_id:
                notion_create_request['properties']['Prev. msg'] = {
                    'relation': [
                        {
                            'id': prev_message.notion_id,
                        },
                    ],
                }
            if reply_to_msg and reply_to_msg.notion_id:
                notion_create_request['properties']['A reply to'] = {
                    'relation': [
                        {
                            'id': reply_to_msg.notion_id,
                        },
                    ],
                }

            notion_page_resp = create_notion_page(notion_create_request)

            message.notion_id = notion_page_resp['id']
            message.notion_synced = True
            message.notion_sync_failed = False
        except Exception:
            message.notion_synced = False
            message.notion_sync_failed = True
            logger.exception('Failed to sync the following message to Notion: %r', message)

        message.save()  # TODO oleksandr: save only updated fields


def _build_username(message: MrbMessage) -> JSONDict:
    if message.username:
        href = f"https://t.me/{message.username}"
        text = f"@{message.username}"

        username_rt = {
            'rich_text': [
                {
                    'href': href,
                    'plain_text': text,
                    'text': {
                        'content': text,
                        'link': {'url': href},
                    },
                    'type': 'text',
                },
            ],
        }
    else:
        text = str(message.user_id)

        username_rt = {
            'rich_text': [
                {
                    'plain_text': text,
                    'text': {
                        'content': text,
                    },
                    'type': 'text',
                },
            ],
        }

    return username_rt
