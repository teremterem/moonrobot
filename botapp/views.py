import json
import logging
from pprint import pformat
from queue import Queue
from threading import Thread
from typing import Union

from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, Bot
from telegram.ext import Dispatcher, CallbackContext, CommandHandler
from telegram.utils.request import Request
from telegram.utils.types import JSONDict

from botapp.models import Dummy

logger = logging.getLogger(__name__)


class MoonRobotRequest(Request):
    def post(self, url: str, data: JSONDict, timeout: float = None) -> Union[JSONDict, bool]:
        logger.warning(f"\nBOT:\n\n%s", pformat(data))  # TODO oleksandr: switch to debug or info

        resp_json = super().post(url, data, timeout=timeout)

        logger.warning(f"\nSERVER RESPONSE:\n\n%s\n", pformat(resp_json))  # TODO oleksandr: switch to debug or info

        return resp_json


bot = Bot(
    settings.MOONROBOT_TELEGRAM_TOKEN,
    request=MoonRobotRequest(),
)
bot.set_webhook(settings.MOONROBOT_TELEGRAM_WEBHOOK)

update_queue = Queue()
dispatcher = Dispatcher(
    bot,
    update_queue,
    workers=settings.MOONROBOT_WORKERS,
)


def start(update: Update, context: CallbackContext) -> None:
    ddd = Dummy(tetetext='tratata')
    ddd.save()
    context.bot.send_message(chat_id=update.effective_chat.id, text="YO YO yo yo yo")


dispatcher.add_handler(CommandHandler('start', start))

thread = Thread(target=dispatcher.start, name='telegram_dispatcher', daemon=True)
thread.start()


@csrf_exempt
def telegram_webhook(request: HttpRequest) -> HttpResponse:
    """
    https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#custom-solution
    """
    body_json = json.loads(request.body)
    logger.warning(f"\nTELEGRAM UPDATE:\n\n%s\n", pformat(body_json))  # TODO oleksandr: switch to debug or info
    update_queue.put(
        Update.de_json(body_json, bot)
    )
    return HttpResponse(status=200)
