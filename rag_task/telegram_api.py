import os
import json
import markdown
import requests
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
from admin_chatbot.models import FileUpload
from rag_task.inference_function import chain_with_source, generate_chat

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TEST_TOKEN")
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'
URL = "https://3309-180-251-229-58.ngrok-free.app/getpost/"

def setwebhook(request):
  response = requests.post(TELEGRAM_API_URL+ "setWebhook?url=" + URL).json()
  
  # Set commands
  commands = [
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
  chat_id = update['message']['chat']['id']
  text = update['message']['text']
  if text == '/info':
    top_5_file = FileUpload.objects.order_by('-count_retrieved')[:5]
    
    answer = ("Kamu bisa bertanya tentang informasi akademik dan non-akademik."
              "Berikut merupakan beberapa contoh hal yang paling sering ditanyakan.\n\n"
              )
    
    for item in top_5_file:
      answer += f"- {item.file_name} \n"
      
    send_message("sendMessage", {
        'chat_id': chat_id,
        'text': answer,
        'parse_mode': 'Markdown',
    })
  else:
    chat_result = generate_chat(text)
    answer = markdown_to_text(chat_result['answer'])
    send_message("sendMessage", {
      'chat_id': chat_id,
      'text': answer,
      # 'parse_mode': 'Markdown',
    })

def send_message(method, data):
  return requests.post(TELEGRAM_API_URL + method, data)

def markdown_to_text(markdown_string):
    # Convert markdown to HTML
    html = markdown.markdown(markdown_string)
    # Use BeautifulSoup to parse the HTML and extract text
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()