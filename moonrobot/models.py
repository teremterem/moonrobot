from django.db import models


class NotionSynchable(models.Model):
    class Meta:
        abstract = True

    notion_synched = models.BooleanField(db_index=True, default=False)
    notion_id = models.TextField(blank=True, null=True)


class MrbUser(NotionSynchable):
    pass


class MrbChat(NotionSynchable):
    pass


class MrbMessage(NotionSynchable):
    # unique_msg_id = models.CharField(max_length=63, unique=True)
    plain_text = models.TextField(blank=True, null=True)
    from_user = models.BooleanField()


class MrbUserMessage(MrbMessage):
    update_payload = models.JSONField(blank=True, null=True)


class MrbBotMessage(MrbMessage):
    url_suffix = models.TextField(blank=True, null=True)
    request_payload = models.JSONField(blank=True, null=True)
    response_payload = models.JSONField(blank=True, null=True)
