from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.template import loader
# from django.contrib.auth import authenticate, login

from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
# from .forms import LoginForm


class CustomLoginView(LoginView):
	template_name = 'login.html';
	redirect_authenticated_user = True

@login_required
def dashboard(request):
    # Konten halaman dashboard
    return render(request, 'dashboard.html')
  
@login_required
def kelolaDokumen(request):
    # Konten halaman dashboard
    return render(request, 'documents.html')

class CustomLogoutView(LogoutView):
    template_name = 'login.html'
    next_page = 'login'