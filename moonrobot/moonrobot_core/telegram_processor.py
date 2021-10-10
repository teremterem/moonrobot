import logging
from pprint import pformat
from queue import Queue
from threading import Thread
from typing import Union

from django.conf import settings
from telegram import Bot
from telegram import Update
from telegram.utils.request import Request
from telegram.utils.types import JSONDict

from botapp.moonrobot_core.update_handler import handle_telegram_update

logger = logging.getLogger(__name__)

update_queue = Queue()


def handle_everything():
    while True:
        update_json = update_queue.get()
        handle_telegram_update_json(update_json)


handler_thread = Thread(target=handle_everything, daemon=True)  # TODO oleksandr: is daemon=True a bad idea ?
handler_thread.start()


class MoonRobotRequest(Request):
    def post(self, url: str, data: JSONDict, timeout: float = None) -> Union[JSONDict, bool]:
        logger.warning('\nBOT:\n\n%s', pformat(data))  # TODO oleksandr: switch to debug or info

        resp_json = super().post(url, data, timeout=timeout)

        logger.warning('\nSERVER RESPONSE:\n\n%s\n', pformat(resp_json))  # TODO oleksandr: switch to debug or info

        return resp_json


bot = Bot(
    settings.MRB_TELEGRAM_TOKEN,
    request=MoonRobotRequest(),
)
bot.set_webhook(settings.MRB_TELEGRAM_WEBHOOK)


def handle_telegram_update_json(update_json: JSONDict):
    logger.warning('\nTELEGRAM UPDATE:\n\n%s\n', pformat(update_json))  # TODO oleksandr: switch to debug or info
    handle_telegram_update(Update.de_json(update_json, bot), bot)
