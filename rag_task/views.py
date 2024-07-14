# Create your views here.
import json
from celery import shared_task
from django.http import JsonResponse
from rag_task.inference_function import generate_chat
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('question', '')
        
        output = generate_chat(query)
        
        return JsonResponse(output)