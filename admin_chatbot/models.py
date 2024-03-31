import os
from django.db import models
from django_celery_results.models import TaskResult

from supabase import create_client
# from django.core.exceptions import ValidationError

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
# Create your models here.
class FileUpload(models.Model):
    file_name = models.CharField(max_length=255, default="NULL", unique=True)
    file_path = models.FileField(upload_to="documents/", default="NULL")
    # total_used = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    task_result = models.OneToOneField(TaskResult, on_delete=models.CASCADE, null=True, blank=True)
    
    def delete(self, *args, **kwargs):
        # Hapus file media terkait saat objek dihapus dari basis data
        if self.file_path:
            # Dapatkan path file
            file_path = self.file_path.path
            # Hapus file dari sistem file
            if os.path.exists(file_path):
                os.remove(file_path)
        super().delete(*args, **kwargs)
    
    # Supabase
    # def delete(self, *args, **kwargs):
    #     if self.file_name:
    #         # Hapus file dari Supabase Storage
    #         supabase.storage.from_('pdf').remove(self.file_name)
    #     super().delete(*args, **kwargs)
        
