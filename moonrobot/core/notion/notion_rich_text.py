import copy
import html
from typing import Collection, List, Optional, Callable

# noinspection PyPackageRequirements
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


def _create_rich_text_entry(text: str, href: Optional[str] = None) -> JSONDict:
    if href:
        link = {'url': href}
    else:
        link = None

    return {
        'annotations': {
            'bold': False,
            'code': False,
            'color': 'default',
            'italic': False,
            'strikethrough': False,
            'underline': False,
        },
        'href': href,
        'plain_text': text,
        'text': {
            'content': text,
            'link': link,
        },
        'type': 'text',
    }


def _clone_rich_text_entry(
        original_entry: JSONDict,
        new_text: str,
        injecter: Optional[Callable[[JSONDict], None]] = None,
) -> JSONDict:
    new_entry = copy.deepcopy(original_entry)
    new_entry['plain_text'] = new_text
    new_entry['text']['content'] = new_text

    if injecter:
        injecter(new_entry)

    return new_entry


def _inject_entity_with_injecter(
        rich_text_entries: Collection[JSONDict],
        entity_start: int,
        entity_length: int,
        injecter: Callable[[JSONDict], None],
):
    entity_end = entity_start + entity_length

    piece_start = 0
    new_entries = []
    for piece_num, entry in enumerate(rich_text_entries):
        text_piece = entry['plain_text']

        piece_end = piece_start + len(text_piece)
        entity_rel_start = entity_start - piece_start
        entity_rel_end = entity_end - piece_start

        if entity_start <= piece_start and piece_end <= entity_end:
            # the entity fully encloses the piece
            new_entries.append(
                _clone_rich_text_entry(entry, text_piece, injecter=injecter),
            )

        elif piece_start < entity_start and entity_end < piece_end:
            # the entity sits inside the piece in such a way that it splits the piece in three
            new_entries.extend([
                _clone_rich_text_entry(entry, text_piece[:entity_rel_start]),
                _clone_rich_text_entry(entry, text_piece[entity_rel_start:entity_rel_end], injecter=injecter),
                _clone_rich_text_entry(entry, text_piece[entity_rel_end:]),
            ])

        elif entity_start <= piece_start < entity_end < piece_end:
            # the entity overlaps with the first half of the piece
            new_entries.extend([
                _clone_rich_text_entry(entry, text_piece[:entity_rel_end], injecter=injecter),
                _clone_rich_text_entry(entry, text_piece[entity_rel_end:]),
            ])

        elif piece_start < entity_start < piece_end <= entity_end:
            # the entity overlaps with the second half of the piece
            new_entries.extend([
                _clone_rich_text_entry(entry, text_piece[:entity_rel_start]),
                _clone_rich_text_entry(entry, text_piece[entity_rel_start:], injecter=injecter),
            ])

        else:
            # the entity does not overlap with the piece (it's either completely before or completely after the piece)
            new_entries.append(entry)

        piece_start = piece_end  # next piece start

    return new_entries


def _inject_entity(
        rich_text_entries: Collection[JSONDict],
        entity: JSONDict,
        original_text: str,
):
    # TODO oleksandr: support all the entity types there are at the intersection of Notion and Telegram
    entity_type = entity['type']
    entity_offset = entity['offset']
    entity_length = entity['length']

    def _simple_injector(entry: JSONDict) -> None:
        entry['annotations'][inj_key] = inj_value

    def _link_injector(entry: JSONDict) -> None:
        entry['href'] = inj_url
        entry['text']['link'] = {'url': inj_url}

    if entity_type == 'bold':
        inj_key = 'bold'
        inj_value = True
        injector = _simple_injector

    elif entity_type == 'italic':
        inj_key = 'italic'
        inj_value = True
        injector = _simple_injector

    elif entity_type == 'strikethrough':
        inj_key = 'strikethrough'
        inj_value = True
        injector = _simple_injector

    elif entity_type == 'underline':
        inj_key = 'underline'
        inj_value = True
        injector = _simple_injector

    elif entity_type == 'code':
        inj_key = 'code'
        inj_value = True
        injector = _simple_injector

    elif entity_type == 'url':
        inj_url = original_text[entity_offset:entity_offset + entity_length]
        injector = _link_injector

    else:
        # unknown entity type => highlight with red background
        inj_key = 'color'
        inj_value = 'red_background'
        injector = _simple_injector

    new_entries = _inject_entity_with_injecter(
        rich_text_entries,
        int(entity_offset),
        int(entity_length),
        injector,
    )
    return new_entries


def rich_text_from_telegram_entities(text: str, entities: Collection[JSONDict]) -> List[JSONDict]:
    rich_text_entries = [_create_rich_text_entry(text)]
    for entity in entities:
        rich_text_entries = _inject_entity(rich_text_entries, entity, text)
    return rich_text_entries
