import os
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView
from django.views.generic.edit import DeleteView
from django.urls import reverse

from django.contrib.auth.views import LoginView, LogoutView
from Chatbot.settings import supabase
from .forms import UploadForm

from .models import FileUpload
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage

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
        
        print(type(file))
        FileSystemStorage(location="/temp").save(file.name, file)
        filepath = "/temp/" + file.name
        
        # Upload file ke Supabase Storage
        with open(filepath, 'rb') as f:
            supabase.storage.from_("pdf").upload(file=f, path=file.name, file_options={"content-type": "application/pdf"})
        
        file_url = supabase.storage.from_('pdf').get_public_url(file)

        form.instance.file_url = file_url
        form.instance.file_name = file.name
        messages.success(self.request, 'File berhasil diunggah!')
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

@login_required
def deletePDF(request, id):
    pdf_data = FileUpload.objects.get(id=id)
    pdf_data.delete()  # Ini akan menghapus file dari Supabase Storage
    return redirect('kelola-dokumen')