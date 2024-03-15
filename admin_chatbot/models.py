import os
from django.db import models

from supabase import create_client
# from django.core.exceptions import ValidationError

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
# Create your models here.
class FileUpload(models.Model):
    file_name = models.CharField(max_length=255, default="NULL")
    file_url = models.URLField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def delete(self, *args, **kwargs):
        if self.file_name:
            # Hapus file dari Supabase Storage
            supabase.storage.from_('pdf').remove(self.file_name)
        super().delete(*args, **kwargs)
        
