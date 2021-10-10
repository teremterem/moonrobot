from django.contrib import admin

from .models import MrbUser, MrbChat, MrbMessage, MrbUserMessage, MrbBotMessage

admin.site.register(MrbUser)
admin.site.register(MrbChat)
admin.site.register(MrbMessage)
admin.site.register(MrbUserMessage)
admin.site.register(MrbBotMessage)
