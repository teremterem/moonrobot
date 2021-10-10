from django.db import models


class User(models.Model):
    pass


class Chat(models.Model):
    pass


class Message(models.Model):
    # class Meta:
    #     abstract = True

    pass


class UserMessage(Message):
    pass


class BotMessage(Message):
    pass
