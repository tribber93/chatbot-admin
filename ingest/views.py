from django.http import HttpResponse
from django.shortcuts import render
from django_celery_results.models import TaskResult

from celery.result import AsyncResult

# Create your views here.

def test(request):
    # send_mail_without_celery()
    # send_email_task.delay()
    # result = test_task.delay(90)
    # print(result.id)
    # tidur.delay(60)
    # return render(request, 'index.html',context={'nama':'Skidipapap','task': result})
    return HttpResponse(f'Test dijalankan! {result.id}')

def result(request):

# Mendapatkan semua objek TaskResult
    all_task_results = TaskResult.objects.all()
        
    # print(all_task_results)
    return render(request, 'index.html',context={'nama':'Skidipapap','task': all_task_results})