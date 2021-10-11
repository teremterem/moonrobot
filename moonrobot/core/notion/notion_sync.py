import time
from threading import Event, Thread

from moonrobot.models import MrbMessage

notion_db_sync_event = Event()


def _sync_db_to_notion_continuously():
    while True:
        notion_db_sync_event.wait()
        notion_db_sync_event.clear()  # TODO oleksandr: this is terrible =\ use some sort of a lock to do this ?
        _sync_db_to_notion()
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
    messages = MrbMessage.objects.filter(notion_synced=True)
    for message in messages:
        print('USER' if message.from_user else 'BOT')
        message.notion_synced = True
        message.save()  # TODO oleksandr: update only changed field
