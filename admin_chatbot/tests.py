from django.conf import settings
from models import FileUpload
from django.db.models import Sum, Count

settings.configure()

# Mendapatkan jumlah total dari kolom count_retrieved
total_count_retrieved = FileUpload.objects.aggregate(total_count_retrieved=Sum('count_retrieved'))['total_count_retrieved'] or 0
print(total_count_retrieved)