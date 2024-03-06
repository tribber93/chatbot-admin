from django.db import models

# Create your models here.
class FileUpload(models.Model):
    file_name = models.CharField(max_length=255, default="NULL")
    file_path = models.FileField(upload_to="documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
