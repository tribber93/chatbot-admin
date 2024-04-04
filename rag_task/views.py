# Create your views here.
import time

from celery import shared_task
from admin_chatbot.models import FileUpload
from django.db.models import F
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rag_task.inference_function import chain, chain_with_source
from .functions import create_retriever


retriever = create_retriever()
instance = FileUpload.objects.all()

chain = chain()
chain_with_source = chain_with_source()

@api_view(['POST'])
def chat(request):
    if request.method == 'POST':
        data = request.data 
        query = data['question']
        
        result = chain_with_source.invoke(query)
        doc_id = result['context'][0].metadata['id']
        
        FileUpload.objects.filter(id=doc_id).update(count_retrieved=F('count_retrieved') + 1)
        
        # return Response({"response": result})
        return Response(result)
    
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