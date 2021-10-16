from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet
from django.http import HttpRequest
# noinspection PyPackageRequirements
from telegram import Update, Message

from moonrobot.core.telegram_bot import get_bot
from moonrobot.models import MrbBot, MrbUser, MrbChat, MrbMessage, MrbUserMessage, MrbBotMessage


def extract_telegram_message(mrb_msg: MrbMessage) -> Message:
    message = None
    if isinstance(mrb_msg, MrbUserMessage):
        update = Update.de_json(mrb_msg.update_payload, get_bot())
        message = update.effective_message
    elif isinstance(mrb_msg, MrbBotMessage):
        message = Message.de_json(mrb_msg.response_payload, get_bot())
    return message


# noinspection PyUnusedLocal
@admin.action(description='Reply')
def reply(modeladmin: 'MrbUserMessageAdmin', request: HttpRequest, queryset: QuerySet) -> None:
    mrb_msg: MrbUserMessage
    for mrb_msg in queryset:
        message = extract_telegram_message(mrb_msg)
        message.reply_text('hello taporld', reply_to_message_id=message.message_id)


class MrbUserMessageAdmin(ModelAdmin):
    actions = [reply]


class MrbBotMessageAdmin(ModelAdmin):
    actions = [reply]


admin.site.register(MrbBot)
admin.site.register(MrbUser)
admin.site.register(MrbChat)
admin.site.register(MrbMessage)
admin.site.register(MrbUserMessage, MrbUserMessageAdmin)
admin.site.register(MrbBotMessage, MrbBotMessageAdmin)
