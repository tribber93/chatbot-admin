import os
import json
import requests
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from rag_task.inference_function import chain_with_source, generate_chat

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'
URL = "https://chatbot.tribber.me/getpost/"

def setwebhook(request):
  response = requests.post(TELEGRAM_API_URL+ "setWebhook?url=" + URL).json()
  return HttpResponse(f"{response}")

@csrf_exempt
def telegram_bot(request):
  if request.method == 'POST':
    update = json.loads(request.body.decode('utf-8'))
    handle_update(update)
    return HttpResponse('ok')
  else:
    return HttpResponseBadRequest('Bad Request')

def handle_update(update):
  chat_id = update['message']['chat']['id']
  text = update['message']['text']
  chat_result = generate_chat(text, clean_response=True)
#   print(chat_result)
  send_message("sendMessage", {
    'chat_id': chat_id,
    'text': chat_result['answer'],
    'parse_mode': 'Markdown',
  })

def send_message(method, data):
  return requests.post(TELEGRAM_API_URL + method, data)