from django.urls import path
from . import views
from .views import CustomLoginView, CustomLogoutView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/kelola-dokumen/', views.kelolaDokumen, name='kelola-dokumen'),
    path('logout/', CustomLogoutView.as_view(), name='logout')
]