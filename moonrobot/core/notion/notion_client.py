import html
import logging
from typing import Collection

import requests
from django.conf import settings
from telegram.utils.types import JSONDict

logger = logging.getLogger(__name__)


def request_notion(uri: str, body_json=None) -> JSONDict:
    url = f"https://api.notion.com/v1/{uri}"

    with requests.post(
            url,
            headers={
                'Authorization': f"Bearer {settings.MRB_NOTION_TOKEN}",
                'Notion-Version': '2021-08-16',
            },
            json=body_json or {},
    ) as resp:
        resp_json = resp.json()

    # logger.warning('\nNOTION: %s\n\n%s\n', url, pformat(resp_json))  # TODO oleksandr: switch to debug or info
    return resp_json


def query_notion_db(database_id: str) -> JSONDict:
    return request_notion(f"databases/{database_id}/query")


def create_notion_page(body: JSONDict) -> JSONDict:
    return request_notion('pages', body_json=body)


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


def fetch_entrypoint_dict() -> JSONDict:
    entrypoints_db_content = query_notion_db(settings.MRB_NOTION_ENTRYPOINTS_DB_ID)

    entrypoints_dict = {}
    for res in entrypoints_db_content['results']:
        key = collect_plain_text(res['properties']['Name']['title'])
        value = collect_html_text(res['properties']['Message']['rich_text'])
        entrypoints_dict[key] = value

    # logger.warning('\nENTRY POINTS:\n\n%s\n', pformat(entrypoints_dict))  # TODO oleksandr: switch to debug or info
    return entrypoints_dict
