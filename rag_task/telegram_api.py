import os
import json
import requests
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rag_task.inference_function import generate_chat
from rag_task.wa_template import get_current_greeting, info

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'
URL = "https://chatbot.tribber.live/getpost/"
# URL = "https://9321-180-253-155-156.ngrok-free.app/getpost/"

def setwebhook(request):
  response = requests.post(TELEGRAM_API_URL+ "setWebhook?url=" + URL).json()
  
  # Set commands
  commands = [
      # {"command": "start", "description": "Selamat datang di UCIC Bot"},
      {"command": "info", "description": "Dapatkan informasi tentang bot"}
  ]
  requests.post(TELEGRAM_API_URL + "setMyCommands", json={"commands": commands})
  
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
  chat = update['message']['chat']
  name = chat['first_name'] + " " + chat['last_name']
  chat_id = chat['id']
  text = update['message']['text']
  if text =='/start':
    answer = get_current_greeting(name)
    send_message("sendMessage", {
        'chat_id': chat_id,
        'text': answer,
        # 'parse_mode': 'Markdown',
    })
  elif text == '/info':
    answer = info()
      
    send_message("sendMessage", {
        'chat_id': chat_id,
        'text': answer,
        # 'parse_mode': 'Markdown',
    })
  else:
    chat_result = generate_chat(text, clean_response=True)#, plain_text=True)
    # chat_result["answer"] = markdown_to_text(chat_result["answer"])
    
    send_message("sendMessage", {
      'chat_id': chat_id,
      'text': chat_result["answer"],
      # 'parse_mode': 'MarkdownV2',
    })

def send_message(method, data):
  return requests.post(TELEGRAM_API_URL + method, data)

def remove_extension(file_name):
    return os.path.splitext(file_name)[0]