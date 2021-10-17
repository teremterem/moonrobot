from typing import Tuple

# noinspection PyPackageRequirements
from telegram import Message


def construct_unique_msg_id(message: Message) -> str:
    # TODO oleksandr: include bot_id
    unique_msg_id = f"{message.chat_id}_{message.message_id}"
    return unique_msg_id


def parse_unique_msg_id(unique_msg_id: str) -> Tuple[int, int]:
    # TODO oleksandr: account for bot_id
    chat_id, msg_id = (int(i) for i in unique_msg_id.split('_'))
    return chat_id, msg_id
