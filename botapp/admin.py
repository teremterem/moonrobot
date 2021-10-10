from django.contrib import admin

from .models import User, Chat, Message, UserMessage, BotMessage

admin.site.register(User)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(UserMessage)
admin.site.register(BotMessage)
