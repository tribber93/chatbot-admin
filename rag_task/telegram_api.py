import os
import json
import markdown
import requests
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from admin_chatbot.models import FileUpload
from rag_task.inference_function import chain_with_source, generate_chat, markdown_to_text

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'
URL = "https://chatbot.tribber.live/getpost/"
# URL = "https://fed3-180-253-155-156.ngrok-free.app/getpost/"

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
  chat_id = update['message']['chat']['id']
  text = update['message']['text']
  if text =='/start':
    answer = ("Hai! Terima kasih telah menghubungi UCIC Bot! 🤖\n"
              "Saya siap membantu Anda mendapatkan informasi yang Anda butuhkan. Berikut beberapa topik yang bisa Anda tanyakan:\n\n"
              "\t1. \t💵 Informasi Biaya\n"
              "\t2. \t🎓 Layanan Akademik\n"
              "\t3. \t🌐 Informasi Kampus\n"
              "\t4. \t♾️ dan lain-lain\n\n"
              "Selamat berinteraksi!\n")
    send_message("sendMessage", {
        'chat_id': chat_id,
        'text': answer,
        # 'parse_mode': 'Markdown',
    })
  elif text == '/info':
    top_5_file = FileUpload.objects.order_by('-count_retrieved')[:10]
    
    answer =  "Kamu bisa bertanya tentang informasi seperti hari libur, biaya kuliah, pendaftaran mahasiswa baru dan sebagainya.\n"
    
    if top_5_file != []:
        answer += "Berikut merupakan beberapa contoh hal yang paling sering ditanyakan.\n\n"
        
        for file in top_5_file:
            file_name = remove_extension(file.file_name)
            answer += f"- {file_name}\n"
      
    send_message("sendMessage", {
        'chat_id': chat_id,
        'text': answer,
        # 'parse_mode': 'Markdown',
    })
  else:
    chat_result = generate_chat(text)#, plain_text=True)
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