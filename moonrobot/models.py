from django.db import models


class NotionSynchable(models.Model):
    class Meta:
        abstract = True


class MrbUser(NotionSynchable):
    pass


class MrbChat(NotionSynchable):
    pass


class MrbMessage(NotionSynchable):
    # unique_msg_id = models.CharField(max_length=63, unique=True)
    pass


class MrbUserMessage(MrbMessage):
    pass


class MrbBotMessage(MrbMessage):
    pass
