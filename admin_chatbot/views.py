import os
import time
from django.http import JsonResponse
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
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from rag_task.tasks import delete_from_vector_db_and_docstore
from django_celery_results.models import TaskResult
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class CustomLoginView(LoginView):
	template_name = 'login.html';
	redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    template_name = 'login.html'
    next_page = 'login'

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    total_retrieved = 0
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mendapatkan jumlah nilai dari kolom field_name
        top_5_retrieved = FileUpload.objects.order_by('-count_retrieved')[:5]
        total_count_retrieved = FileUpload.objects.aggregate(total=Sum('count_retrieved'))['total'] or 0
        context = {
            "top_5_retrieved": top_5_retrieved,
            "total_retrieved":  total_count_retrieved
        }
        
        return context

    # def get(self, request, **kwargs):
    #     context = super().get_context_data(**kwargs)
        
    #     print(context.values().keys())
    #     return render(request, self.template_name)
    
class KelolaDokumenView(LoginRequiredMixin, CreateView):
    model = FileUpload
    form_class = UploadForm
    template_name = "kelola_dokumen.html"
    success_url = reverse_lazy("kelola-dokumen")
    paginate_by = 3
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ambil data FileUpload dari basis data
        files = FileUpload.objects.select_related('task_result').order_by('-uploaded_at')  # Anda dapat menggunakan query yang sesuai di sini
        
        paginator = Paginator(files, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            files = paginator.page(page)
        except PageNotAnInteger:
            files = paginator.page(1)
        except EmptyPage:
            files = paginator.page(paginator.num_pages)
        
        
        context['files'] = files
        return context
    
    def form_valid(self, form):
        
        file = form.cleaned_data['file_path']
        if not any(file.name.endswith(ext) for ext in settings.ALLOWED_EXTENSIONS):
            messages.error(self.request, f'File harus berformat salah satu dari: {", ".join(settings.ALLOWED_EXTENSIONS)}!')
            return self.form_invalid(form)
        if file.size > 5 * 1024 * 1024:
            messages.error(self.request, 'Ukuran file tidak boleh lebih dari 5 MB!')
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
    try:
        task = pdf_data.task_result_id
        TaskResult.objects.get(id=task).delete()
    except TaskResult.DoesNotExist:
        pass
    pdf_data.delete() 
    messages.success(request, f'File {pdf_data.file_name} berhasil dihapus!')
    return redirect('kelola-dokumen')

@login_required
def dashboard_chart(request):
    data = FileUpload.objects.all()
    top_5 = FileUpload.objects.order_by('-count_retrieved')[:5]
    total_top_5 = top_5.aggregate(total=Sum('count_retrieved'))['total'] or 0
    total_count_retrieved = FileUpload.objects.aggregate(total=Sum('count_retrieved'))['total'] or 0
    lainnya = total_count_retrieved - total_top_5
    labels = [item.file_name for item in top_5] + ["Lainnya"]
    values = [item.count_retrieved for item in top_5] + [lainnya]
    
    chart_data = {
        'labels': labels,
        'values': values,
        'chart_type': 'doughnut' # any chart type line, bar, ects
    }
    
    return JsonResponse(chart_data)

@login_required
def get_docs_data(request):
    page = request.GET.get('page', 1)
    per_page = 10  # Jumlah item per halaman
    file_uploads = FileUpload.objects.select_related('task_result').order_by('-uploaded_at').all().values()
    
    paginator = Paginator(file_uploads, per_page)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    
    for item in items:
        task_results = TaskResult.objects.filter(id=item['task_result_id']).values('status')
        item['status'] = task_results[0]['status']
    
    items_list = list(items)
    
    response = {
        'items': items_list,
        'num_pages': paginator.num_pages,
        'current_page': items.number,
        'has_next': items.has_next(),
        'has_previous': items.has_previous(),
    }
    return JsonResponse(response, safe=False)