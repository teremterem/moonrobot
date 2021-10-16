import time
from threading import Event, Thread

from django.conf import settings

from moonrobot.core.notion.notion_client import create_notion_page
from moonrobot.core.notion.notion_rich_text import rich_text_from_telegram_entities
from moonrobot.models import MrbMessage

notion_db_sync_event = Event()


def _sync_db_to_notion_continuously():
    while True:
        notion_db_sync_event.wait()
        notion_db_sync_event.clear()  # TODO oleksandr: this is terrible =\ use some sort of a lock to do this ?

        # TODO oleksandr: guard with try/except
        _sync_db_to_notion()  # TODO oleksandr: sync only one object, not all at once (no loops inside)
        time.sleep(1)  # TODO oleksandr: make it configurable ?


_notion_sync_thread = Thread(
    name='_notion_sync_thread',
    target=_sync_db_to_notion_continuously,
    daemon=True,  # TODO oleksandr: is daemon=True a bad idea ?
)
_notion_sync_thread.start()  # TODO oleksandr: use a pool of workers ?


# TODO oleksandr: think what kind of racing conditions are possible (decide on transaction isolation mechanism)
# TODO oleksandr: use transaction.atomic ?
def _sync_db_to_notion():
    messages = MrbMessage.objects.filter(notion_synced=False)  # TODO oleksandr: order by message timestamp
    for message in messages:  # TODO oleksandr: get rid of this loop - only one item per second or so ! :(
        notion_page_resp = create_notion_page({
            'parent': {  # TODO oleksandr: move this inside of notion_client.py
                'database_id': settings.MRB_NOTION_MESSAGES_DB_ID,
            },
            'properties': {
                'Name': [
                    {
                        'text': {
                            'content': 'USER' if message.from_user else 'BOT',
                        },
                    },
                ],
                'Message': rich_text_from_telegram_entities(message.plain_text or '', message.text_entities or []),
                # 'Timestamp': {
                #     'number': message.sent_timestamp,
                # },
            },
        })

        message.notion_id = notion_page_resp['id']
        message.notion_synced = True
        message.save()  # TODO oleksandr: update only changed field
