import os

from telegram.ext import Updater, CommandHandler

MOONROBOT_TELEGRAM_TOKEN = os.environ['MOONROBOT_TELEGRAM_TOKEN']
MOONROBOT_NOTION_TOKEN = os.environ['MOONROBOT_NOTION_TOKEN']

updater = Updater(token=MOONROBOT_TELEGRAM_TOKEN)
dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


dispatcher.add_handler(CommandHandler('start', start))

if __name__ == '__main__':
    updater.start_polling()
