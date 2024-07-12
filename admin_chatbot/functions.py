from fuzzywuzzy import fuzz
from django.utils import timezone
from django.db.models import Sum, Count

from admin_chatbot.models import ChatHistory, FileUpload


def get_top_dokumen_last_7_days():
    today = timezone.now()
    last_week = today - timezone.timedelta(days=6)  # Menghitung 6 hari yang lalu untuk mendapatkan rentang 7 hari terakhir

    # Query untuk mendapatkan data ChatHistory dari 7 hari terakhir
    chat_data_last_7_days = ChatHistory.objects.filter(timestamp__range=[last_week, today], is_answered=True)

    # Grupkan berdasarkan file_upload dan hitung jumlah kemunculannya, lalu urutkan secara descending
    top_document = chat_data_last_7_days.values('file_upload_id').annotate(count=Count('file_upload_id')).order_by('-count').first()
    
    # Jika tidak ada data dalam rentang waktu tersebut, kembalikan None atau pesan lain yang sesuai
    if not top_document:
        return {"message": "Data Tidak Tersedia"}
        # return {"message": "Tidak ada dokumen dalam 7 hari terakhir"}
    
    try:
        file_id = top_document['file_upload_id']
        file_upload = FileUpload.objects.get(id=file_id)
        top_document['file_name'] = file_upload.file_name
    except FileUpload.DoesNotExist:
        return {"message": "Data Tidak Tersedia"}
    # file_id = top_document['file_upload_id']
    # top_document['file_name'] = FileUpload.objects.get(id=file_id).file_name
    
    return top_document


def find_matching_context(output, context1, context2):
    score1 = fuzz.ratio(output, context1.page_content)
    score2 = fuzz.ratio(output, context2.page_content)
    
    if score1 > score2:
        return context1
    elif score2 > score1:
        return context2
    else:
        return context1