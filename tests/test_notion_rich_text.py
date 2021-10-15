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

    (
            '“mention” (@username)\n'
            '\n'
            '“hashtag” (#hashtag)\n'
            '\n'
            '“cashtag” ($USD)\n'
            '\n'
            '“bot_command” (/start@jobs_bot)\n'
            '\n'
            '“url” (https://telegram.org)\n'
            '\n'
            '“email” (do-not-reply@telegram.org)\n'
            '\n'
            '“phone_number” (+1-212-555-0123)\n'
            '\n'
            '“bold” (bold text)\n'
            '\n'
            '“italic” (italic text)\n'
            '\n'
            '“underline” (underlined text) ???\n'
            '\n'
            '“strikethrough” (strikethrough text) ???\n'
            '\n'
            '“code” (monowidth string)\n'
            '\n'
            '“pre” (\n'
            'monowidth block\n'
            ') ?????\n'
            '\n'
            '“text_link” (for clickable text URLs)\n'
            '\n'
            '“text_mention” (for users without usernames) ???',

            [{'length': 9, 'offset': 11, 'type': 'mention'},
             {'length': 8, 'offset': 34, 'type': 'hashtag'},
             {'length': 4, 'offset': 56, 'type': 'cashtag'},
             {'length': 15, 'offset': 78, 'type': 'bot_command'},
             {'length': 20, 'offset': 103, 'type': 'url'},
             {'length': 25, 'offset': 135, 'type': 'email'},
             {'length': 15, 'offset': 179, 'type': 'phone_number'},
             {'length': 9, 'offset': 205, 'type': 'bold'},
             {'length': 11, 'offset': 227, 'type': 'italic'},
             {'length': 15, 'offset': 254, 'type': 'underline'},
             {'length': 18, 'offset': 293, 'type': 'strikethrough'},
             {'length': 16, 'offset': 326, 'type': 'code'},
             {'length': 17, 'offset': 352, 'type': 'pre'},
             {'length': 23,
              'offset': 391,
              'type': 'text_link',
              'url': 'https://www.google.com/'},
             {'length': 27,
              'offset': 433,
              'type': 'text_mention',
              'user': {'first_name': 'Oleksandr',
                       'id': 210723289,
                       'is_bot': False,
                       'language_code': 'en',
                       'last_name': 'Tereshchenko',
                       'username': 'username2'}}],

            [{'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': '“mention” (',
              'text': {'content': '“mention” (',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': 'https://t.me/username',
              'plain_text': '@username',
              'text': {'content': '@username',
                       'link': {'url': 'https://t.me/username'}},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ')\n\n“hashtag” (',
              'text': {'content': ')\n'
                                  '\n'
                                  '“hashtag” (',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'red_background',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': '#hashtag',
              'text': {'content': '#hashtag',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ')\n\n“cashtag” (',
              'text': {'content': ')\n'
                                  '\n'
                                  '“cashtag” (',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'red_background',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': '$USD',
              'text': {'content': '$USD',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ')\n\n“bot_command” (',
              'text': {'content': ')\n'
                                  '\n'
                                  '“bot_command” '
                                  '(',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'red_background',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': '/start@jobs_bot',
              'text': {'content': '/start@jobs_bot',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ')\n\n“url” (',
              'text': {'content': ')\n\n“url” (',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': 'https://telegram.org',
              'plain_text': 'https://telegram.org',
              'text': {'content': 'https://telegram.org',
                       'link': {'url': 'https://telegram.org'}},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ')\n\n“email” (',
              'text': {'content': ')\n\n“email” (',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': 'mailto:do-not-reply@telegram.org',
              'plain_text': 'do-not-reply@telegram.org',
              'text': {'content': 'do-not-reply@telegram.org',
                       'link': {'url': 'mailto:do-not-reply@telegram.org'}},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ')\n'
                            '\n'
                            '“phone_number” (',
              'text': {'content': ')\n'
                                  '\n'
                                  '“phone_number” '
                                  '(',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'red_background',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': '+1-212-555-0123',
              'text': {'content': '+1-212-555-0123',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ')\n\n“bold” (',
              'text': {'content': ')\n\n“bold” (',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': True,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': 'bold text',
              'text': {'content': 'bold text',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ')\n\n“italic” (',
              'text': {'content': ')\n'
                                  '\n'
                                  '“italic” (',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': True,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': 'italic text',
              'text': {'content': 'italic text',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ')\n\n“underline” (',
              'text': {'content': ')\n'
                                  '\n'
                                  '“underline” (',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': True},
              'href': None,
              'plain_text': 'underlined text',
              'text': {'content': 'underlined '
                                  'text',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ') ???\n'
                            '\n'
                            '“strikethrough” (',
              'text': {'content': ') ???\n'
                                  '\n'
                                  '“strikethrough” '
                                  '(',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': True,
                              'underline': False},
              'href': None,
              'plain_text': 'strikethrough text',
              'text': {'content': 'strikethrough '
                                  'text',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ') ???\n\n“code” (',
              'text': {'content': ') ???\n'
                                  '\n'
                                  '“code” (',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': True,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': 'monowidth string',
              'text': {'content': 'monowidth '
                                  'string',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ')\n\n“pre” (',
              'text': {'content': ')\n\n“pre” (',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'red_background',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': '\nmonowidth block\n',
              'text': {'content': '\n'
                                  'monowidth '
                                  'block\n',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ') ?????\n'
                            '\n'
                            '“text_link” (',
              'text': {'content': ') ?????\n'
                                  '\n'
                                  '“text_link” (',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': 'https://www.google.com/',
              'plain_text': 'for clickable text '
                            'URLs',
              'text': {'content': 'for clickable '
                                  'text URLs',
                       'link': {'url': 'https://www.google.com/'}},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ')\n'
                            '\n'
                            '“text_mention” (',
              'text': {'content': ')\n'
                                  '\n'
                                  '“text_mention” '
                                  '(',
                       'link': None},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': 'https://t.me/username2',
              'plain_text': 'for users without '
                            'usernames',
              'text': {'content': 'for users '
                                  'without '
                                  'usernames',
                       'link': {'url': 'https://t.me/username2'}},
              'type': 'text'},
             {'annotations': {'bold': False,
                              'code': False,
                              'color': 'default',
                              'italic': False,
                              'strikethrough': False,
                              'underline': False},
              'href': None,
              'plain_text': ') ???',
              'text': {'content': ') ???',
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
