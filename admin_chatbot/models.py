import os
from django.db import models

# Create your models here.
class FileUpload(models.Model):
    file_name = models.CharField(max_length=255, default="NULL")
    file_path = models.FileField(upload_to="documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def delete(self, *args, **kwargs):
        # Hapus file media terkait saat objek dihapus dari basis data
        if self.file_path:
            # Dapatkan path file
            file_path = self.file_path.path
            # Hapus file dari sistem file
            if os.path.exists(file_path):
                os.remove(file_path)
        super().delete(*args, **kwargs)
