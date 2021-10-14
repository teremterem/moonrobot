import html
from typing import Collection

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
