import json
import logging
from pprint import pformat
from queue import Queue
from threading import Thread
from typing import Union

from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from telegram import Update, Bot, ParseMode
from telegram.ext import Dispatcher, CallbackContext, MessageHandler, Filters
from telegram.utils.request import Request
from telegram.utils.types import JSONDict

from botapp.notion_client import fetch_entrypoint_dict

logger = logging.getLogger(__name__)


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

update_queue = Queue()
dispatcher = Dispatcher(
    bot,
    update_queue,
    workers=settings.MRB_WORKERS,
)


def handle_anything(update: Update, context: CallbackContext) -> None:
    entrypoints_dict = fetch_entrypoint_dict()

    if update.effective_message:
        msg = entrypoints_dict.get(update.effective_message.text)
        if msg:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                parse_mode=ParseMode.HTML,
                text=msg,
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                parse_mode=ParseMode.HTML,
                text="""
<b>bold</b>, <strong>bold</strong>
<i>italic</i>, <em>italic</em>
<u>underline</u>, <ins>underline</ins>
<s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
<b>bold <i>italic bold <s>italic bold strikethrough</s> <u>underline italic bold</u></i> bold</b>
<a href="http://www.example.com/">inline URL</a>
<a href="tg://user?id=210723289">inline mention of a user</a>
<code>inline fixed-width code</code>
<pre>pre-formatted fixed-width code block</pre>
<pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>
                """,
            )


# covers everything except for what CallbackQueryHandler covers (any other exceptions?)
dispatcher.add_handler(MessageHandler(Filters.all, handle_anything))

thread = Thread(target=dispatcher.start, name='telegram_dispatcher', daemon=True)
thread.start()


@csrf_exempt
def telegram_webhook(request: HttpRequest) -> HttpResponse:
    """
    https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#custom-solution
    """
    body_json = json.loads(request.body)
    logger.warning('\nTELEGRAM UPDATE:\n\n%s\n', pformat(body_json))  # TODO oleksandr: switch to debug or info
    update_queue.put(
        Update.de_json(body_json, bot)
    )
    return HttpResponse(status=200)
