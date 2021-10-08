import json
import logging
from pprint import pformat
from queue import Queue
from threading import Thread

from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, Bot
from telegram.ext import Dispatcher, CallbackContext, CommandHandler

from botapp.models import Dummy

logger = logging.getLogger(__name__)

bot = Bot(settings.MOONROBOT_TELEGRAM_TOKEN)
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
    logger.warning(f"TELEGRAM UPDATE:\n%s", pformat(body_json))  # TODO oleksandr: switch to debug or info
    update_queue.put(
        Update.de_json(body_json, bot)
    )
    return HttpResponse(status=200)
