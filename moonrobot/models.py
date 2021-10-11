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
    plain_text = models.TextField(null=True, blank=True)


class MrbUserMessage(MrbMessage):
    update_payload = models.JSONField(null=True, blank=True)


class MrbBotMessage(MrbMessage):
    url_suffix = models.TextField(null=True, blank=True)
    request_payload = models.JSONField(null=True, blank=True)
    response_payload = models.JSONField(null=True, blank=True)
