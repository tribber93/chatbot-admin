# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rag_task.inference_function import chain, chain_with_source
from admin_chatbot.models import FileUpload
from django.db.models import F


chain = chain()
chain_with_source = chain_with_source()

@api_view(['POST'])
def chat(request):
    if request.method == 'POST':
        data = request.data  
        
        result = chain.invoke(data['question'])
        # if result['context'] != []:
        #     local_source = result['context'][0].metadata['source'].split('\\')[-1]
        #     source = local_source.replace('_', ' ')

        #     FileUpload.objects.filter(file_name=source).update(count_retrieved=F('count_retrieved') + 1)
        
        return Response(result)