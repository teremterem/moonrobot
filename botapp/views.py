# import json
#
# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
#
#
# @csrf_exempt
# def telegram_webhook(request):
#     # logger.info(f'{str(request.body)} <=== {type(request.body)}')
#     body_json = json.loads(request.body)
#     # logger.info(f'{str(body_json)} <=== {type(body_json)}')
#     dispatch_telegram_update(body_json)
#     return HttpResponse(status=200)
#
#
# # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#custom-solution
# def dispatch_telegram_update(json_request):
#     plur.plur_bot.update_queue.put(
#         Update.de_json(json_request, plur.plur_bot.bot)
#     )
#     # XXX do we need to suppress exceptions with try/catch here ?
