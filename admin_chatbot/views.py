import os
import time
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView

from django.contrib.auth.views import LoginView, LogoutView
from Chatbot.settings import supabase
from .forms import UploadForm

from .models import FileUpload
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from ingest.tasks import test_task
from django_celery_results.models import TaskResult

class CustomLoginView(LoginView):
	template_name = 'login.html';
	redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    template_name = 'login.html'
    next_page = 'login'

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get(self, request):
        return render(request, self.template_name)
    
class KelolaDokumenView(LoginRequiredMixin, CreateView):
    model = FileUpload
    form_class = UploadForm
    template_name = "documents.html"
    success_url = reverse_lazy("kelola-dokumen")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ambil data FileUpload dari basis data
        files = FileUpload.objects.select_related('task_result')  # Anda dapat menggunakan query yang sesuai di sini
        context['files'] = files
        return context
    
    def form_valid(self, form):
        file = form.cleaned_data['file_path']
        if not file.name.endswith('.pdf'):
            messages.error(self.request, 'File harus berformat PDF!')
            return self.form_invalid(form)
        if file.size > 10 * 1024 * 1024:
            messages.error(self.request, 'Ukuran file tidak boleh lebih dari 10 MB!')
            return self.form_invalid(form)
        if FileUpload.objects.filter(file_name=file.name).exists():
            messages.error(self.request, 'File dengan nama yang sama sudah ada!')
            return self.form_invalid(form)
        
        # print(type(file))
        FileSystemStorage(location="/temp").save(file.name, file)
        filepath = "/temp/" + file.name
        
        # Upload file ke Supabase Storage
        with open(filepath, 'rb') as f:
            supabase.storage.from_("pdf").upload(file=f, path=file.name, file_options={"content-type": "application/pdf"})
        
        file_url = supabase.storage.from_('pdf').get_public_url(file)
        form.instance.file_url = file_url
        form.instance.file_name = file.name
        
        # print("File URL:", file_url)
        task = test_task.delay(60)
        time.sleep(0.5)
        task_result_instance = TaskResult.objects.get(task_id=task)
        form.instance.task_result = task_result_instance
        messages.success(self.request, 'File berhasil diunggah!')
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

@login_required
def deletePDF(request, id):
    pdf_data = FileUpload.objects.get(id=id)
    task = pdf_data.task_result_id
    TaskResult.objects.get(id=task).delete()
    pdf_data.delete()  # Ini akan menghapus file dari Supabase Storage
    return redirect('kelola-dokumen')