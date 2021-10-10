import logging

from telegram import Bot
from telegram import Update, ParseMode

from moonrobot.core.notion_client import fetch_entrypoint_dict

logger = logging.getLogger(__name__)


def handle_telegram_update(update: Update, bot: Bot) -> None:
    entrypoints_dict = fetch_entrypoint_dict()

    if update.effective_message:
        msg = entrypoints_dict.get(update.effective_message.text)
        if msg:
            bot.send_message(
                chat_id=update.effective_chat.id,
                parse_mode=ParseMode.HTML,
                text=msg,
            )
        else:
            bot.send_message(
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
