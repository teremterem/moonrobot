from django.conf import settings
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet
from django.http import HttpRequest
# noinspection PyPackageRequirements
from telegram import Update, Message, ParseMode

from moonrobot.core.notion.notion_client import query_notion_db, update_notion_page
from moonrobot.core.notion.notion_rich_text import collect_html_text
from moonrobot.core.telegram_bot import get_bot
from moonrobot.core.utils import parse_unique_msg_id
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


# noinspection PyUnusedLocal
@admin.action(description='Set Telegram webhook')
def set_telegram_webhook(modeladmin: 'MrbBotMessageAdmin', request: HttpRequest, queryset: QuerySet) -> None:
    get_bot().set_webhook(settings.MRB_TELEGRAM_WEBHOOK)


# noinspection PyUnusedLocal
@admin.action(description='Process outbox')
def process_outbox(modeladmin: 'MrbBotMessageAdmin', request: HttpRequest, queryset: QuerySet) -> None:
    # TODO oleksandr: store it in local DB
    # TODO oleksandr: account for pagination
    messages_db_content = query_notion_db(
        settings.MRB_NOTION_MESSAGES_DB_ID,
        body={
            'filter': {
                'property': 'Status',
                'select': {
                    'equals': 'Outbox',
                },
            },
        },
    )

    for outbox_msg in messages_db_content['results']:
        notion_page_id = outbox_msg['id']

        # TODO oleksandr: is it cheating to use a rollup instead of the original relation ?
        notion_answer_with_msgs = outbox_msg['properties']['Answer with msg']['rollup']['array']
        answer_with_msgs = [collect_html_text(m['rich_text']) for m in notion_answer_with_msgs]

        mrb_msg = MrbMessage.objects.filter(notion_id=notion_page_id).first()
        if mrb_msg and mrb_msg.unique_msg_id:
            chat_id, msg_id = parse_unique_msg_id(mrb_msg.unique_msg_id)

            for answer_with_msg in answer_with_msgs:
                get_bot().send_message(
                    chat_id,
                    answer_with_msg,
                    parse_mode=ParseMode.HTML,
                    reply_to_message_id=msg_id,
                )

            if answer_with_msgs:
                # TODO oleksandr: schedule this as synchronization
                update_notion_page(notion_page_id, {
                    'properties': {
                        'Status': {
                            'select': {
                                'name': 'Answered',
                            },
                        },
                    },
                })


class MrbBotAdmin(ModelAdmin):
    actions = [process_outbox, set_telegram_webhook]


class MrbUserMessageAdmin(ModelAdmin):
    actions = [reply]


class MrbBotMessageAdmin(ModelAdmin):
    actions = [reply]


admin.site.register(MrbBot, MrbBotAdmin)
admin.site.register(MrbUser)
admin.site.register(MrbChat)
admin.site.register(MrbMessage)
admin.site.register(MrbUserMessage, MrbUserMessageAdmin)
admin.site.register(MrbBotMessage, MrbBotMessageAdmin)
