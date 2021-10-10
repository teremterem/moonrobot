import logging
from pprint import pformat
from queue import Queue
from threading import Thread
from typing import Union

from django.conf import settings
from telegram import Bot, Message
from telegram import Update
from telegram.utils.request import Request
from telegram.utils.types import JSONDict

from moonrobot.core.update_handler import handle_telegram_update
from moonrobot.models import MrbBotMessage, MrbUserMessage

logger = logging.getLogger(__name__)

update_queue = Queue()


def _handle_everything():
    while True:
        update_json = update_queue.get()
        handle_telegram_update_json(update_json)


_handler_thread = Thread(target=_handle_everything, daemon=True)  # TODO oleksandr: is daemon=True a bad idea ?
_handler_thread.start()  # TODO oleksandr: use a pool of workers ?
_bot = None


def get_bot():  # TODO oleksandr: is it thread safe ?
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

        logger.warning('\nBOT: %s\n\n%s', url_suffix, pformat(data))  # TODO oleksandr: switch to debug or info

        resp_json = super().post(url, data, timeout=timeout)

        if url_suffix != '/setWebhook':
            resp_msg = Message.de_json(resp_json, get_bot())
            mrb_bot_message = MrbBotMessage(
                plain_text=resp_msg.text,
                url_suffix=url_suffix,
                request_payload=data,
                response_payload=resp_json,
            )
            mrb_bot_message.save()

        logger.warning('\nSERVER RESPONSE:\n\n%s\n', pformat(resp_json))  # TODO oleksandr: switch to debug or info

        return resp_json


def handle_telegram_update_json(update_json: JSONDict):
    logger.warning('\nTELEGRAM UPDATE:\n\n%s\n', pformat(update_json))  # TODO oleksandr: switch to debug or info

    update = Update.de_json(update_json, get_bot())

    mrb_user_message = MrbUserMessage(
        plain_text=update.effective_message.text,
        update_payload=update_json,
    )
    mrb_user_message.save()

    handle_telegram_update(update, get_bot())
