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
            msg = entrypoints_dict.get('moonrobot_default_response')
            if msg:
                bot.send_message(
                    chat_id=update.effective_chat.id,
                    parse_mode=ParseMode.HTML,
                    text=msg,
                )
