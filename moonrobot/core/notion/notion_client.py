import logging
from pprint import pformat

import requests
from django.conf import settings
# noinspection PyPackageRequirements
from telegram.utils.types import JSONDict

from moonrobot.core.notion.notion_rich_text import collect_plain_text, collect_html_text

logger = logging.getLogger(__name__)


def request_notion(uri: str, method: str = 'post', body=None) -> JSONDict:
    url = f"https://api.notion.com/v1/{uri}"

    with requests.request(
            method,
            url,
            headers={
                'Authorization': f"Bearer {settings.MRB_NOTION_TOKEN}",
                'Notion-Version': '2021-08-16',
            },
            json=body or {},
    ) as resp:
        resp_json = resp.json()

    if logger.isEnabledFor(logging.DEBUG):
        # TODO oleksandr: use a different logging level if there is an error
        logger.debug('\nNOTION: %s\n\n%s\n', url, pformat(resp_json))
    return resp_json


def query_notion_db(database_id: str, body=None) -> JSONDict:
    return request_notion(f"databases/{database_id}/query", body=body)


def create_notion_page(body: JSONDict) -> JSONDict:
    return request_notion('pages', body=body)


def update_notion_page(page_id: str, body: JSONDict) -> JSONDict:
    return request_notion(f"pages/{page_id}", method='patch', body=body)


def fetch_entrypoint_dict() -> JSONDict:
    # TODO oleksandr: account for pagination; schedule as synchronization
    entrypoints_db_content = query_notion_db(settings.MRB_NOTION_ENTRYPOINTS_DB_ID)

    # TODO oleksandr: store it in local DB
    entrypoints_dict = {}
    for res in entrypoints_db_content['results']:
        key = collect_plain_text(res['properties']['Name']['title'])
        value = collect_html_text(res['properties']['Message']['rich_text'])
        entrypoints_dict[key] = value

    # if logger.isEnabledFor(logging.DEBUG):
    #     logger.debug('\nENTRY POINTS:\n\n%s\n', pformat(entrypoints_dict))
    return entrypoints_dict
