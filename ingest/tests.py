import os
from django.test import TestCase
from dotenv import load_dotenv

from supabase import create_client

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
import os
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Chatbot.settings')
settings.configure()

# load_dotenv(override=True)
# # Create your tests here.
# print(os.getenv('EMAIL_HOST_PASSWORD'))

# response = supabase.table('admin_chatbot_fileupload').select("*").execute()
# print(response.data[0])

# filepath = "media/documents/Pengumuman Her registrasi dan KRS Semester Ganjil Tahun Akademik 2023-2024 - Web MyUCIC.pdf"
# path_on_supastorage = "Pengumuman Her registrasi dan KRS Semester Ganjil Tahun Akademik 2023-2024 - Web MyUCIC.pdf"  # Define the variable "path_on_supastorage"

# with open(filepath, 'rb') as f:
#     supabase.storage.from_("pdf").upload(file=f, path=path_on_supastorage, file_options={"content-type": "application/pdf"})
# supabase.storage.from_('pdf').remove("Kompetensi - Fajar Gema Ramadhan.pdf")
from django_celery_results.models import TaskResult

# Mendapatkan semua objek TaskResult
all_task_results = TaskResult.objects.all()
print(all_task_results )
# Mendapatkan hasil task dengan ID tertentu
# task_result = TaskResult.objects.get(id=4)

# # Menampilkan status hasil task
# print(task_result.status)

# # Menampilkan waktu mulai dan selesai
# print(task_result.date_done)
# print(task_result.date_started)

# # Menampilkan hasil dari task jika sudah selesai
# print(task_result.result)
