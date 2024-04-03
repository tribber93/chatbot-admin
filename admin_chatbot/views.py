import os
import time
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.views.generic import CreateView

from django.contrib.auth.views import LoginView, LogoutView
# import Chatbot
# from Chatbot.settings import supabase
from .forms import UploadForm

from .models import FileUpload
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from rag_task.tasks import delete_from_vector_db_and_docstore
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
        
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'documents'))  # Simpan di dalam folder uploads
        
        form.instance.file_name = form.cleaned_data['file_name']
        messages.success(self.request, 'File berhasil diunggah!')
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    
@login_required
def deletePDF(request, id):
    pdf_data = FileUpload.objects.get(id=id)
    path = pdf_data.file_path.path
    # print(os.path.join(settings.MEDIA_ROOT, path))
    delete_from_vector_db_and_docstore(os.path.join(settings.MEDIA_ROOT, path))
    task = pdf_data.task_result_id
    TaskResult.objects.get(id=task).delete()
    pdf_data.delete() 
    messages.success(request, f'File {pdf_data.file_name} berhasil dihapus!')
    return redirect('kelola-dokumen')