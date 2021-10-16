from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet
from django.http import HttpRequest
# noinspection PyPackageRequirements
from telegram import Update

from moonrobot.core.telegram_bot import get_bot
from moonrobot.models import MrbBot, MrbUser, MrbChat, MrbMessage, MrbUserMessage, MrbBotMessage


# noinspection PyUnusedLocal
@admin.action(description='Reply')
def reply(modeladmin: 'MrbUserMessageAdmin', request: HttpRequest, queryset: QuerySet) -> None:
    msg: MrbUserMessage
    for msg in queryset:
        update = Update.de_json(msg.update_payload, get_bot())
        update.effective_message.reply_text('hello taporld')


class MrbUserMessageAdmin(ModelAdmin):
    actions = [reply]


admin.site.register(MrbBot)
admin.site.register(MrbUser)
admin.site.register(MrbChat)
admin.site.register(MrbMessage)
admin.site.register(MrbUserMessage, MrbUserMessageAdmin)
admin.site.register(MrbBotMessage)
