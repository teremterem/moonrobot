import logging
import os
from queue import Queue
from threading import Thread

from django.conf import settings
# noinspection PyPackageRequirements
from telegram import Bot

from moonrobot.core.telegram_processor import handle_telegram_update_json, MoonRobotRequest

logger = logging.getLogger(__name__)

HARDCODED_USER_ID = int(os.getenv('HARDCODED_USER_ID') or '0')  # for quick experimentation
HARDCODED_CHAT_ID = HARDCODED_USER_ID  # for quick experimentation

update_queue = Queue()


def _handle_everything() -> None:
    while True:
        update_json = update_queue.get()
        handle_telegram_update_json(update_json, get_bot())


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
        mrb_request = MoonRobotRequest()
        _bot = Bot(
            settings.MRB_TELEGRAM_TOKEN,
            request=mrb_request,
        )
        mrb_request.bot = _bot

        # TODO oleksandr: this fails unit tests - do something about it
        _bot.set_webhook(settings.MRB_TELEGRAM_WEBHOOK)

    return _bot


# TODO oleksandr: figure how to only load the bot when server is started and not during othe operations like
#  `python manage.py makemigrations`
get_bot()
