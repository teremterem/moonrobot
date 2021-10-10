import json
import logging

from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt

from moonrobot.core.telegram_processor import update_queue

logger = logging.getLogger(__name__)


@csrf_exempt
def telegram_webhook(request: HttpRequest) -> HttpResponse:
    body_json = json.loads(request.body)
    update_queue.put(body_json)
    return HttpResponse(status=200)
