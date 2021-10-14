from typing import Collection, List

import pytest
# noinspection PyPackageRequirements
from telegram import MessageEntity, Bot
# noinspection PyPackageRequirements
from telegram.utils.types import JSONDict

# noinspection PyProtectedMember
from moonrobot.core.notion.notion_rich_text import rich_text_from_telegram_annotations, _inject_entity


@pytest.mark.parametrize('text_pieces, entity, expected', [
    (
            ['so', 'me ', 'three ', 'pieces', ' of text', '..', '.'],

            {'length': 11, 'offset': 8},

            ['so', 'me ', 'thr', 'ee ', 'pieces', ' o', 'f text', '..', '.'],
    ),
])
def test_inject_entity(
        text_pieces: Collection[str],
        entity: JSONDict,
        expected: Collection[str],
) -> None:
    actual = _inject_entity(text_pieces, entity)
    assert expected == actual


# noinspection DuplicatedCode
@pytest.mark.parametrize('text, entities, expected', [
    (
            'hello bold italic bold world',

            [{'length': 5, 'offset': 6, 'type': 'bold'},
             {'length': 11, 'offset': 11, 'type': 'bold'},
             {'length': 6, 'offset': 11, 'type': 'italic'}],

            [{'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': 'hello ',
              'text': {'content': 'hello ',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': True,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': 'bold ',
              'text': {'content': 'bold ',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': True,
                              'code': False,
                              'color': 'default',
                              'italic': True,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': 'italic',
              'text': {'content': 'italic',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': True,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ' bold',
              'text': {'content': ' '
                                  'bold',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ' world',
              'text': {'content': ' '
                                  'world',
                       'link': None},
              'type': 'text'}],
    ),
])
def test_rich_text_from_telegram_annotations(
        text: str,
        entities: List[JSONDict],
        expected: Collection[JSONDict],
        fake_bot: Bot,
) -> None:
    entities_ptb = MessageEntity.de_list(entities, fake_bot)
    actual = rich_text_from_telegram_annotations(text, entities_ptb)
    assert expected == actual
