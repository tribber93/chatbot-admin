import os
from django.db import models
from django_celery_results.models import TaskResult

from supabase import create_client
# from django.core.exceptions import ValidationError

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
# Create your models here.
class FileUpload(models.Model):
    file_name = models.CharField(max_length=255, default="NULL", unique=True)
    file_url = models.URLField(blank=True)
    # total_used = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    task_result = models.OneToOneField(TaskResult, on_delete=models.CASCADE, null=True, blank=True)
    
    def delete(self, *args, **kwargs):
        if self.file_name:
            # Hapus file dari Supabase Storage
            supabase.storage.from_('pdf').remove(self.file_name)
        super().delete(*args, **kwargs)
        
