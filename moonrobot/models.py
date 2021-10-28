from django.db import models


class NotionSyncable(models.Model):
    class Meta:
        abstract = True

    notion_synced = models.BooleanField(db_index=True, default=False)
    notion_id = models.TextField(blank=True, null=True, db_index=True)  # TODO oleksandr: unique=True ?


class MrbBot(NotionSyncable):
    pass


class MrbUser(NotionSyncable):
    pass


class MrbChat(NotionSyncable):
    pass


class MrbMessage(NotionSyncable):
    unique_msg_id = models.CharField(max_length=63, unique=True)  # TODO oleksandr: include bot_id
    plain_text = models.TextField(blank=True, null=True)
    text_entities = models.JSONField(blank=True, null=True)

    # TODO oleksandr: get rid of this field when you start employing a relation to MrbChat and MrbUser
    user_display_name = models.TextField(blank=True, null=True)

    from_user = models.BooleanField()
    sent_timestamp = models.BigIntegerField()

    def __str__(self):
        norm_text = ' '.join((self.plain_text or '').split())

        preview_limit = 100
        if len(norm_text) > preview_limit:
            norm_text = norm_text[:preview_limit - 3] + '...'

        result = f"[{'USER' if self.from_user else 'BOT'} #{self.id}]: {norm_text}"
        return result


class MrbUserMessage(MrbMessage):
    update_payload = models.JSONField(blank=True, null=True)


class MrbBotMessage(MrbMessage):
    url_suffix = models.TextField(blank=True, null=True)
    request_payload = models.JSONField(blank=True, null=True)
    response_payload = models.JSONField(blank=True, null=True)
