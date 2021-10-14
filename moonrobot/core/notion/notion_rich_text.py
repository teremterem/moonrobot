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


def _inject_entity(text_pieces: Collection[str], entity: JSONDict):
    entity_start = int(entity['offset'])
    entity_length = int(entity['length'])
    entity_end = entity_start + entity_length

    piece_start = 0
    new_text_pieces = []
    for piece_num, text_piece in enumerate(text_pieces):
        piece_end = piece_start + len(text_piece)
        entity_rel_start = entity_start - piece_start
        entity_rel_end = entity_end - piece_start

        if entity_start <= piece_start and piece_end <= entity_end:
            # the entity fully encloses the piece
            new_text_pieces.append(text_piece)  # TODO mark this piece

        elif piece_start < entity_start and entity_end < piece_end:
            # the entity sits inside the piece in such a way that it splits the piece in three
            new_text_pieces.extend([
                text_piece[:entity_rel_start],
                text_piece[entity_rel_start:entity_rel_end],  # TODO mark this piece
                text_piece[entity_rel_end:],
            ])

        elif entity_start <= piece_start < entity_end < piece_end:
            # the entity overlaps with the first half of the piece
            new_text_pieces.extend([
                text_piece[:entity_rel_end],  # TODO mark this piece
                text_piece[entity_rel_end:],
            ])

        elif piece_start < entity_start < piece_end <= entity_end:
            # the entity overlaps with the second half of the piece
            new_text_pieces.extend([
                text_piece[:entity_rel_start],
                text_piece[entity_rel_start:],  # TODO mark this piece
            ])

        else:
            # the entity does not overlap with the piece (it's either completely before or completely after the piece)
            new_text_pieces.append(text_piece)

        piece_start = piece_end  # next piece start

    return new_text_pieces


def rich_text_from_telegram_annotations(text: str, entities: Collection[MessageEntity]) -> List[JSONDict]:
    return [
        {
            'annotations': {
                'bold': False,
                'code': False,
                'color': 'default',
                'italic': False,
                'strikethrough': False,
                'underline': False,
            },
            'href': None,
            'plain_text': text,
            'text': {
                'content': text,
                'link': None,
            },
            'type': 'text',
        },
    ]
