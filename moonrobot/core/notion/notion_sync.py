import time
from threading import Thread, Event

from django.conf import settings
# noinspection PyPackageRequirements
from telegram import Update, Message
# noinspection PyPackageRequirements
from telegram.utils.types import JSONDict

from moonrobot.core.notion.notion_client import create_notion_page
from moonrobot.core.notion.notion_rich_text import rich_text_from_telegram_entities
from moonrobot.models import MrbMessage, MrbUserMessage, MrbBotMessage

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

    messages = MrbMessage.objects.filter(notion_synced=False).order_by('sent_timestamp')
    for message in messages:  # TODO oleksandr: get rid of this loop - only one item per second or so ! :(
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
                    'number': message.sent_timestamp,
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
                    }
                ],
            }

        notion_page_resp = create_notion_page(notion_create_request)

        message.notion_id = notion_page_resp['id']
        message.notion_synced = True
        message.save()  # TODO oleksandr: update only changed field


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
