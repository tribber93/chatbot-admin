import os
import pytz
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.views.generic import CreateView
from django.utils.translation import gettext as _

from django.contrib.auth.views import LoginView, LogoutView

from admin_chatbot.functions import get_top_dokumen_last_7_days
from .forms import UploadForm

from .models import ChatHistory, FileUpload
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
# from rag_task.qdrantdb import delete_from_vector_db_and_docstore
from rag_task.chromadb import delete_a_chunk_doc
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
        top_dokumen_last_7_days = get_top_dokumen_last_7_days()
        
        context = {
            "top_5_retrieved": top_5_retrieved,
            "total_retrieved":  total_count_retrieved,
            "top_7_days": top_dokumen_last_7_days
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
        if file.size > 3 * 1024 * 1024:
            messages.error(self.request, 'Ukuran file tidak boleh lebih dari 3 MB!')
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
    
    ######### chromadb
    delete_a_chunk_doc(os.path.join(settings.MEDIA_ROOT, path))
    ######### qdrant 
    # delete_from_vector_db_and_docstore(os.path.join(settings.MEDIA_ROOT, path))
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

def get_chat_frequency_last_7_days(request):
    today = timezone.now()
    jakarta_timezone = pytz.timezone('Asia/Jakarta')
    today_jakarta = today.astimezone(jakarta_timezone)
    last_week = today_jakarta - timezone.timedelta(days=7)

    # Ambil data chat dalam rentang waktu 7 hari terakhir
    chat_history_data = ChatHistory.objects.filter(timestamp__range=[last_week, today])
    
    # Buat dictionary dengan kunci sebagai tanggal dan nilai awal 0 untuk setiap hari dalam 7 hari terakhir
    date_range = { (today_jakarta - timezone.timedelta(days=i)).date(): {'count': 0, 'day_name': ''} for i in range(8) }

    # Perbarui dictionary dengan data dari query
    for chat_record in chat_history_data:
        local_time = chat_record.timestamp.astimezone(jakarta_timezone)
        
        # Ambil bagian tanggal dari timestamp yang sudah dikonversi
        date = local_time.date()

        # Tambahkan 1 untuk jumlah pesan pada tanggal tersebut di dalam dictionary
        if date in date_range:
            date_range[date]['count'] += 1

    # Tambahkan nama hari dalam Bahasa Indonesia ke dalam dictionary
    for date, data in date_range.items():
        day_name = _(date.strftime('%A'))  # Menggunakan fungsi gettext untuk menerjemahkan nama hari
        data['day_name'] = day_name

    # Konversi dictionary ke list of tuples dan urutkan berdasarkan tanggal
    chat_frequency_list = sorted(date_range.items())

    # Siapkan data JSON untuk dikirim sebagai respons
    json_data = [{'tanggal': date.strftime('%Y-%m-%d'), 'jumlah': data['count'], 'nama_hari': data['day_name']} for date, data in chat_frequency_list]

    return JsonResponse(json_data, safe=False)

