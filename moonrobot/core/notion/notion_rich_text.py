import html
from typing import Collection, List

# noinspection PyPackageRequirements
from telegram import MessageEntity
# noinspection PyPackageRequirements
from telegram.utils.types import JSONDict


def collect_plain_text(rich_text_list: Collection[JSONDict]) -> str:
    text = ''.join([i['plain_text'] for i in rich_text_list])
    return text


def collect_html_text(rich_text_list: Collection[JSONDict]) -> str:
    def decorate_piece(piece):
        piece_text = html.escape(piece['text']['content'])
        piece_annotations = piece['annotations']

        if piece_annotations['code']:
            piece_text = f"<code>{piece_text}</code>"
        if piece_annotations['bold']:
            piece_text = f"<b>{piece_text}</b>"
        if piece_annotations['italic']:
            piece_text = f"<i>{piece_text}</i>"
        if piece_annotations['strikethrough']:
            piece_text = f"<s>{piece_text}</s>"
        if piece_annotations['underline']:
            piece_text = f"<u>{piece_text}</u>"

        piece_link = (piece['text']['link'] or {}).get('url')
        if piece_link:
            piece_text = f"<a href=\"{piece_link}\">{piece_text}</a>"

        return piece_text

    text = ''.join([decorate_piece(i) for i in rich_text_list])
    return text


# TODO TODO TODO
dummy = [{'annotations': {'bold': False,
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
          'type': 'text'}]


def rich_text_from_telegram_annotations(text: str, entities: Collection[MessageEntity]) -> List[JSONDict]:
    return dummy  # TODO TODO TODO
