import os
import time
from django.conf import settings
from django.db import models
from django.shortcuts import redirect
from django.http import HttpResponseServerError
from django_celery_results.models import TaskResult
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from rag_task.tasks import ingest_data

from supabase import create_client
# from django.core.exceptions import ValidationError

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
# Create your models here.
class FileUpload(models.Model):
    file_name = models.CharField(max_length=255, default="NULL", unique=True)
    file_path = models.FileField(upload_to="documents/", default="NULL")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    task_result = models.OneToOneField(TaskResult, on_delete=models.CASCADE, null=True, blank=True)
    count_retrieved = models.IntegerField(default=0)
    
    def delete(self, *args, **kwargs):
        # Hapus file media terkait saat objek dihapus dari basis data
        if self.file_path:
            # Dapatkan path file
            file_path = self.file_path.path
            # Hapus file dari sistem file
            if os.path.exists(file_path):
                os.remove(file_path)
        super().delete(*args, **kwargs)
    
@receiver(post_save, sender=FileUpload)
def process_ingest_data(sender, instance, created, **kwargs):
    if created:  # Pastikan proses hanya dijalankan saat objek baru dibuat
        path = instance.file_path.path
        path = os.path.join(settings.MEDIA_ROOT, path)
        task = ingest_data.delay(path, instance.id)
        
        # Tetapkan batas waktu maksimum untuk menunggu hasil task
        max_wait_time = 30  # misalnya, 60 detik
        start_time = time.time()  # Waktu awal untuk menghitung batas waktu
        
        # Menunggu hingga hasil task tersedia
        while True:
            if time.time() - start_time > max_wait_time:
                # Jika batas waktu maksimum tercapai, kembalikan HttpResponseServerError
                pdf_data = FileUpload.objects.get(id=instance.id)
                pdf_data.delete()
                raise HttpResponseServerError("Timeout saat menunggu hasil tugas dari Celery.")
            
            try:
                task_result_instance = TaskResult.objects.get(task_id=task.id)
                instance.task_result = task_result_instance
                instance.save()  # Simpan instance setelah menetapkan task_result
                break
            except ObjectDoesNotExist:
                # time.sleep(1)
                continue
        
        return redirect('kelola-dokumen')
        # try:
        #     task = ingest_data.delay(path, instance.id)
        #     time.sleep(1)
        #     task_result_instance = TaskResult.objects.get(task_id=task)
        #     instance.task_result = task_result_instance
        #     instance.save()  # Simpan instance setelah menetapkan task_result
        # except Exception as e:
        #     print(e)
        #     raise e
        # finally:
        #     return redirect('kelola-dokumen')
        
class ChatHistory(models.Model):
    file_upload = models.ForeignKey(FileUpload, on_delete=models.SET_NULL, null=True, related_name='chat_history')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_answered = models.BooleanField(default=False)