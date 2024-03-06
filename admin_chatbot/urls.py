from django.urls import path
from . import views
from .views import CustomLoginView, CustomLogoutView, DashboardView, KelolaDokumenView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/kelola-dokumen/', KelolaDokumenView.as_view(), name='kelola-dokumen'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]