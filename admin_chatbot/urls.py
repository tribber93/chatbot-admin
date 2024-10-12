from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static
from .views import CustomLoginView, CustomLogoutView, DashboardView, KelolaDokumenView, SetToken

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard-data/', views.dashboard_chart, name='dashboard-data'),
    path('chat-frequency/', views.get_chat_frequency_last_7_days, name='chat-frequency'),
    path('docs-data/', views.get_docs_data, name='docs-data'),
    path('dashboard/kelola-dokumen/', KelolaDokumenView.as_view(), name='kelola-dokumen'),
    path('dashboard/set-token-wa/', SetToken.as_view(), name='set-token-wa'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('dashboard/kelola-dokumen/delete/<int:id>/', view=views.deletePDF, name='delete_file'),
]

# Tambahkan URL untuk menyajikan file media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)