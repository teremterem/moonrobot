from django.db import models


class MrbUser(models.Model):
    pass


class MrbChat(models.Model):
    pass


class MrbMessage(models.Model):
    # unique_msg_id = models.CharField(max_length=63, unique=True)
    pass


class MrbUserMessage(MrbMessage):
    pass


class MrbBotMessage(MrbMessage):
    pass
