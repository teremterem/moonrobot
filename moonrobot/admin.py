from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet
from django.http import HttpRequest

from moonrobot.core.telegram_processor import get_bot, HARDCODED_CHAT_ID
from moonrobot.models import MrbBot, MrbUser, MrbChat, MrbMessage, MrbUserMessage, MrbBotMessage


# noinspection PyUnusedLocal
@admin.action(description='Sync the bot(s) with Notion')
def sync_with_notion(modeladmin: 'MrbBotAdmin', request: HttpRequest, queryset: QuerySet) -> None:
    get_bot().send_message(HARDCODED_CHAT_ID, 'hello taporld')


class MrbBotAdmin(ModelAdmin):
    actions = [sync_with_notion]


admin.site.register(MrbBot, MrbBotAdmin)
admin.site.register(MrbUser)
admin.site.register(MrbChat)
admin.site.register(MrbMessage)
admin.site.register(MrbUserMessage)
admin.site.register(MrbBotMessage)
