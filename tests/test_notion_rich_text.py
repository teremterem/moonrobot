from typing import Collection, List, Any

import pytest
# noinspection PyPackageRequirements
# noinspection PyPackageRequirements
from telegram.utils.types import JSONDict

# noinspection PyProtectedMember
from moonrobot.core.notion.notion_rich_text import rich_text_from_telegram_entities, _inject_entity_with_injecter, \
    _create_rich_text_entry


class Marked:
    def __init__(self, text: str) -> None:
        self.text = text


@pytest.mark.parametrize('text_pieces, entity, expected', [
    (  # 0
            ['aaa', 'bbb', 'ccc'],
            {'length': 2, 'offset': 0},
            [Marked('aa'), 'a', 'bbb', 'ccc'],
    ),
    (  # 1
            ['aaa', 'bbb', 'ccc'],
            {'length': 3, 'offset': 0},
            [Marked('aaa'), 'bbb', 'ccc'],
    ),
    (  # 2
            ['aaa', 'bbb', 'ccc'],
            {'length': 4, 'offset': 0},
            [Marked('aaa'), Marked('b'), 'bb', 'ccc'],
    ),
    (  # 3
            ['aaa', 'bbb', 'ccc'],
            {'length': 6, 'offset': 0},
            [Marked('aaa'), Marked('bbb'), 'ccc'],
    ),
    (  # 4
            ['aaa', 'bbb', 'ccc'],
            {'length': 9, 'offset': 0},
            [Marked('aaa'), Marked('bbb'), Marked('ccc')],
    ),
    (  # 5
            ['aaa', 'bbb', 'ccc'],
            {'length': 1, 'offset': 4},
            ['aaa', 'b', Marked('b'), 'b', 'ccc'],
    ),
    (  # 6
            ['aaa', 'bbb', 'ccc'],
            {'length': 4, 'offset': 4},
            ['aaa', 'b', Marked('bb'), Marked('cc'), 'c'],
    ),
    (  # 7
            ['aaa', 'bbb', 'ccc'],
            {'length': 2, 'offset': 6},
            ['aaa', 'bbb', Marked('cc'), 'c'],
    ),
    (  # 8
            ['aaa', 'bbb', 'ccc'],
            {'length': 3, 'offset': 6},
            ['aaa', 'bbb', Marked('ccc')],
    ),
    (  # 9
            ['aaa', 'bbb', 'ccc'],
            {'length': 2, 'offset': 7},
            ['aaa', 'bbb', 'c', Marked('cc')],
    ),
    (  # 10
            ['so', 'me ', 'three ', 'pieces', ' of text', '..', '.'],
            {'length': 11, 'offset': 8},
            ['so', 'me ', 'thr', Marked('ee '), Marked('pieces'), Marked(' o'), 'f text', '..', '.'],
    ),
])
def test_inject_entity_with_injecter(
        text_pieces: Collection[str],
        entity: JSONDict,
        expected: Collection[Any],
) -> None:
    rich_text_entries = [_create_rich_text_entry(t) for t in text_pieces]
    expected_entries = []

    for e in expected:
        is_marked = isinstance(e, Marked)

        expected_entry = _create_rich_text_entry(e.text if is_marked else e)
        expected_entry['annotations']['bold'] = is_marked
        expected_entries.append(expected_entry)

    def _make_bold(entry: JSONDict) -> None:
        entry['annotations']['bold'] = True

    actual_entries = _inject_entity_with_injecter(rich_text_entries, entity['offset'], entity['length'], _make_bold)
    assert expected_entries == actual_entries


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
def test_rich_text_from_telegram_entities(
        text: str,
        entities: List[JSONDict],
        expected: Collection[JSONDict],
) -> None:
    actual = rich_text_from_telegram_entities(text, entities)
    assert expected == actual
