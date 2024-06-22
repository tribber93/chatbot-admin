# Create your views here.
import json
import time

from celery import shared_task
from admin_chatbot.models import FileUpload
from django.db.models import F
from django.http import JsonResponse
from rag_task.inference_function import chain, chain_with_source, is_unanswerable_response
from .functions import create_retriever
from django.views.decorators.csrf import csrf_exempt


retriever = create_retriever()
instance = FileUpload.objects.all()

chain = chain()
chain_with_source = chain_with_source()


@csrf_exempt
def chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('question', '')
        
        result = chain_with_source.invoke(query)
        
        output = {
            "question": query,
            "answer": result['answer'],
        }
        
        if result['context'] != []:
            if not is_unanswerable_response(result['answer']):
                doc_id = result['context'][0].metadata['id']
                
                FileUpload.objects.filter(id=doc_id).update(count_retrieved=F('count_retrieved') + 1)
            
        return JsonResponse(output)
    
@shared_task
def update_count(query):
    start_time = time.time()
    tes = retriever.get_relevant_documents(query)
    if tes == []:
        return 

    doc_id = tes[0].metadata['id']
    FileUpload.objects.filter(id=doc_id).update(count_retrieved=F('count_retrieved') + 1)
    end_time = time.time()

    # Hitung lama waktu yang dibutuhkan
    duration = end_time - start_time
    return f"Lama mendapatkan konteks: {duration} detik"