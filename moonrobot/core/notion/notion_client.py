import logging
from pprint import pformat

import requests
from django.conf import settings
# noinspection PyPackageRequirements
from telegram.utils.types import JSONDict

from moonrobot.core.notion.notion_rich_text import collect_plain_text, collect_html_text

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

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('\nNOTION: %s\n\n%s\n', url, pformat(resp_json))
    return resp_json


def query_notion_db(database_id: str) -> JSONDict:
    return request_notion(f"databases/{database_id}/query")


def create_notion_page(body: JSONDict) -> JSONDict:
    return request_notion('pages', body_json=body)


def fetch_entrypoint_dict() -> JSONDict:
    entrypoints_db_content = query_notion_db(settings.MRB_NOTION_ENTRYPOINTS_DB_ID)

    entrypoints_dict = {}
    for res in entrypoints_db_content['results']:
        key = collect_plain_text(res['properties']['Name']['title'])
        value = collect_html_text(res['properties']['Message']['rich_text'])
        entrypoints_dict[key] = value

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('\nENTRY POINTS:\n\n%s\n', pformat(entrypoints_dict))
    return entrypoints_dict
