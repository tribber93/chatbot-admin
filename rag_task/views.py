# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rag_task.inference_function import chain


chain = chain()

@api_view(['POST'])
def chat(request):
    if request.method == 'POST':
        data = request.data  # Mendapatkan data yang diterima dalam permintaan
        # Lakukan inferensi menggunakan model Anda
        # Prediksi hasil
        result = chain.invoke(data['question'])
        # result = your_model.predict(data)
        # Kembalikan hasil dalam respons API
        return Response({'result': result})