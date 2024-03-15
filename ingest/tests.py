import os
from django.test import TestCase
from dotenv import load_dotenv

from supabase import create_client

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))


# load_dotenv(override=True)
# # Create your tests here.
# print(os.getenv('EMAIL_HOST_PASSWORD'))

# response = supabase.table('admin_chatbot_fileupload').select("*").execute()
# print(response.data[0])

# filepath = "media/documents/Pengumuman Her registrasi dan KRS Semester Ganjil Tahun Akademik 2023-2024 - Web MyUCIC.pdf"
# path_on_supastorage = "Pengumuman Her registrasi dan KRS Semester Ganjil Tahun Akademik 2023-2024 - Web MyUCIC.pdf"  # Define the variable "path_on_supastorage"

# with open(filepath, 'rb') as f:
#     supabase.storage.from_("pdf").upload(file=f, path=path_on_supastorage, file_options={"content-type": "application/pdf"})
supabase.storage.from_('pdf').remove("Kompetensi - Fajar Gema Ramadhan.pdf")