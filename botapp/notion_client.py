import html
import logging
from pprint import pformat

import requests
from django.conf import settings
from telegram.utils.types import JSONDict

logger = logging.getLogger(__name__)


def request_notion(uri: str, body_json=None) -> JSONDict:
    url = f"https://api.notion.com/v1/{uri}"

    with requests.post(
            url,
            headers={
                'Authorization': f"Bearer {settings.MOONROBOT_NOTION_TOKEN}",
                'Notion-Version': '2021-08-16',
            },
            json=body_json or {},
    ) as resp:
        resp_json = resp.json()

    logger.warning('\nNOTION: %s\n\n%s\n', url, pformat(resp_json))  # TODO oleksandr: switch to debug or info
    return resp_json


def query_notion_db(database_id: str) -> JSONDict:
    return request_notion(f"databases/{database_id}/query")


def collect_plain_text(rich_text_list):
    text = ''.join([i['plain_text'] for i in rich_text_list])
    return text


def collect_html_text(rich_text_list):
    text = ''.join([html.escape(i['plain_text']) for i in rich_text_list])
    return text


def fetch_entrypoint_dict():
    entrypoints_db_content = query_notion_db(settings.MRBT_ENTRYPOINTS_DB_ID)

    entrypoints_dict = {}
    for res in entrypoints_db_content['results']:
        key = collect_plain_text(res['properties']['Name']['title'])
        value = collect_html_text(res['properties']['Message']['rich_text'])
        entrypoints_dict[key] = value

    logger.warning('\nENTRY POINTS:\n\n%s\n', pformat(entrypoints_dict))  # TODO oleksandr: switch to debug or info
    return entrypoints_dict
