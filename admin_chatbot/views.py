import imp
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from multiprocessing import context
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.views.generic import CreateView

from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from .forms import UploadForm

from .models import FileUpload


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
        files = FileUpload.objects.all()  # Anda dapat menggunakan query yang sesuai di sini
        context['files'] = files
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'File berhasil diupload.')
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, 'File gagal diupload. Pastikan nama file tidak ada yang sama dan format file harus .pdf.')
        return response