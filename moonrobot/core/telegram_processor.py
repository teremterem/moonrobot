import logging
from pprint import pformat
from typing import Union, Optional

from django.conf import settings
# noinspection PyPackageRequirements
from telegram import Bot, Message, User
# noinspection PyPackageRequirements
from telegram import Update
# noinspection PyPackageRequirements
from telegram.utils.request import Request
# noinspection PyPackageRequirements
from telegram.utils.types import JSONDict

from moonrobot.core.notion.notion_sync import notion_db_sync_event
from moonrobot.core.update_handler import handle_telegram_update
from moonrobot.core.utils import construct_unique_msg_id
from moonrobot.models import MrbBotMessage, MrbUserMessage

logger = logging.getLogger(__name__)


class MoonRobotRequest(Request):
    def __init__(self, bot: Optional[Bot] = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot  # TODO oleksandr: PTB deprecated doing this - how to refactor ?

    def post(self, url: str, data: JSONDict, timeout: float = None) -> Union[JSONDict, bool]:
        url_suffix = url.split(settings.MRB_TELEGRAM_TOKEN)[-1]

        if logger.isEnabledFor(logging.INFO):
            logger.info('\nBOT: %s\n\n%s', url_suffix, pformat(data))

        resp_json = super().post(url, data, timeout=timeout)

        if url_suffix != '/setWebhook':
            resp_msg = Message.de_json(resp_json, self.bot)
            mrb_bot_message = MrbBotMessage(
                unique_msg_id=construct_unique_msg_id(resp_msg),
                plain_text=resp_msg.text,

                # TODO oleksandr: fetch from the original dict instead ?
                text_entities=[e.to_dict() for e in resp_msg.entities],

                from_user=False,
                sent_timestamp=resp_msg.to_dict()['date'],  # TODO oleksandr: fetch from the original dict instead ?
                url_suffix=url_suffix,
                request_payload=data,
                response_payload=resp_json,
            )
            mrb_bot_message.save()

        if logger.isEnabledFor(logging.INFO):
            logger.info('\nSERVER RESPONSE:\n\n%s\n', pformat(resp_json))

        notion_db_sync_event.set()  # TODO oleksandr: use some sort of a lock to do this ?
        return resp_json


def extract_user_display_name(telegram_user: User) -> str:
    display_name = [name for name in (telegram_user.first_name, telegram_user.last_name) if name]
    display_name = ' '.join(display_name)

    if display_name:
        return display_name

    user_handle_or_id = f"@{telegram_user.username}" if telegram_user.username else telegram_user.id
    return user_handle_or_id


def handle_telegram_update_json(update_json: JSONDict, bot: Bot) -> None:
    update = None

    # noinspection PyBroadException
    try:
        if logger.isEnabledFor(logging.INFO):
            logger.info('\nTELEGRAM UPDATE:\n\n%s\n', pformat(update_json))

        update = Update.de_json(update_json, bot)

        mrb_user_message = MrbUserMessage(
            unique_msg_id=construct_unique_msg_id(update.effective_message),
            plain_text=update.effective_message.text,
            text_entities=[e.to_dict() for e in update.effective_message.entities],
            from_user=True,
            user_display_name=extract_user_display_name(update.effective_user),
            username=update.effective_user.username,
            user_id=update.effective_user.id,

            # TODO oleksandr: fetch from the original dict instead ?
            sent_timestamp=update.effective_message.to_dict()['date'],

            update_payload=update_json,
        )
        mrb_user_message.save()

        notion_db_sync_event.set()  # TODO oleksandr: use some sort of a lock to do this ?

        handle_telegram_update(update, bot)
    except Exception:
        logger.exception('EXCEPTION WHILE PROCESSING A TELEGRAM UPDATE')

        # noinspection PyBroadException
        try:
            if update and update.effective_chat:
                update.effective_chat.send_message('Ouch! Something went wrong 🤖')
        except Exception:
            logger.debug('EXCEPTION WHILE REPORTING AN EXCEPTION', exc_info=True)
