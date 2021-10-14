import logging
from pprint import pformat
from queue import Queue
from threading import Thread
from typing import Union

from django.conf import settings
# noinspection PyPackageRequirements
from telegram import Bot, Message
# noinspection PyPackageRequirements
from telegram import Update
# noinspection PyPackageRequirements
from telegram.utils.request import Request
# noinspection PyPackageRequirements
from telegram.utils.types import JSONDict

from moonrobot.core.notion.notion_sync import notion_db_sync_event
from moonrobot.core.update_handler import handle_telegram_update
from moonrobot.models import MrbBotMessage, MrbUserMessage

logger = logging.getLogger(__name__)

update_queue = Queue()


def _handle_everything() -> None:
    while True:
        update_json = update_queue.get()
        handle_telegram_update_json(update_json)


_telegram_handler_thread = Thread(
    name='_telegram_handler_thread',
    target=_handle_everything,
    daemon=True,  # TODO oleksandr: is daemon=True a bad idea ?
)
_telegram_handler_thread.start()  # TODO oleksandr: use a pool of workers ?
_bot = None


def get_bot() -> Bot:  # TODO oleksandr: is it thread safe ?
    global _bot

    if not _bot:
        _bot = Bot(
            settings.MRB_TELEGRAM_TOKEN,
            request=MoonRobotRequest(),
        )
        _bot.set_webhook(settings.MRB_TELEGRAM_WEBHOOK)

    return _bot


class MoonRobotRequest(Request):
    def post(self, url: str, data: JSONDict, timeout: float = None) -> Union[JSONDict, bool]:
        url_suffix = url.split(settings.MRB_TELEGRAM_TOKEN)[-1]

        logger.info('\nBOT: %s\n\n%s', url_suffix, pformat(data))

        resp_json = super().post(url, data, timeout=timeout)

        if url_suffix != '/setWebhook':
            resp_msg = Message.de_json(resp_json, get_bot())
            mrb_bot_message = MrbBotMessage(
                plain_text=resp_msg.text,
                from_user=False,
                url_suffix=url_suffix,
                request_payload=data,
                response_payload=resp_json,
            )
            mrb_bot_message.save()
            # for ent in resp_msg.entities:
            #     print(
            #         str(ent.offset).rjust(10, ' '),
            #         str(ent.offset + ent.length).rjust(10, ' '),
            #         ent.type.rjust(30, ' '),
            #     )
            #     # pprint(ent.to_dict())

        logger.info('\nSERVER RESPONSE:\n\n%s\n', pformat(resp_json))

        notion_db_sync_event.set()  # TODO oleksandr: use some sort of a lock to do this ?
        return resp_json


# TODO oleksandr: figure how to only load the bot when server is started and not during othe operations like
#  `python manage.py makemigrations`
get_bot()


def handle_telegram_update_json(update_json: JSONDict) -> None:
    bot = get_bot()
    update = None

    # noinspection PyBroadException
    try:
        logger.info('\nTELEGRAM UPDATE:\n\n%s\n', pformat(update_json))

        update = Update.de_json(update_json, bot)

        mrb_user_message = MrbUserMessage(
            plain_text=update.effective_message.text,
            from_user=True,
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
