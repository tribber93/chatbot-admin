import os
from django.db import models
# from django.core.exceptions import ValidationError

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
    
    # def clean(self):
    #     super().clean()

    #     # Validasi ekstensi file
    #     if not self.file_path.name.lower().endswith('.pdf'):
    #         raise ValidationError({'file_path': 'Format file harus .pdf.'})

    #     # Validasi ukuran file
    #     max_size = 10 * 1024 * 1024  # 10MB
    #     if self.file_path.size > max_size:
    #         raise ValidationError({'file_path': 'Ukuran file tidak boleh lebih dari 10MB.'})

    #     # Validasi nama file
    #     if FileUpload.objects.exclude(pk=self.pk).filter(file_name=self.file_name).exists():
    #         raise ValidationError('Nama file sudah ada.')
