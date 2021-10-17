import logging
import os

# noinspection PyPackageRequirements
from telegram import Bot
# noinspection PyPackageRequirements
from telegram import Update, ParseMode

from moonrobot.core.notion.notion_client import fetch_entrypoint_dict

logger = logging.getLogger(__name__)

# TODO oleksandr: get rid of these
HARDCODED_USER_ID = int(os.getenv('HARDCODED_USER_ID') or '0')  # for quick experimentation
HARDCODED_CHAT_ID = HARDCODED_USER_ID  # for quick experimentation


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
                # text='thanks',
                #                 text="""
                # <b>bold</b>, <strong>bold</strong>
                # <i>italic</i>, <em>italic</em>
                # <u>underline</u>, <ins>underline</ins>
                # <s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
                # <b>bold <i>italic bold <s>italic bold strikethrough</s> <u>underline italic bold</u></i> bold</b>
                # <a href="https://www.example.com/">inline URL</a>
                # <a href="tg://user?id=210723289">inline mention of a user</a>
                # <code>inline fixed-width code</code>
                # <pre>pre-formatted fixed-width code block</pre>
                # <pre><code class="language-python">pre-formatted fixed-width code block written in the Python
                # programming language
                # </code></pre>
                #                 """,
                text="""
“mention” (@username)

“hashtag” (#hashtag)

“cashtag” ($USD)

“bot_command” (/start@jobs_bot)

“url” (https://telegram.org)

“email” (do-not-reply@telegram.org)

“phone_number” (+1-212-555-0123)

“bold” (<b>bold text</b>)

“italic” (<i>italic text</i>)

“underline” (<u>underlined text</u>) ???

“strikethrough” (<s>strikethrough text</s>) ???

“code” (<code>monowidth string</code>)

“pre” (<pre>
monowidth block
</pre>) ?????

“text_link” (<a href="https://www.google.com/">for clickable text URLs</a>)

“text_mention” (<a href="tg://user?id=210723289">for users without usernames</a>) ???
                """
            )
