from django.http import HttpResponse
from django.shortcuts import render

from .helper import send_mail_without_celery

from ingest.tasks import send_email_task, tidur, add, test_task

# Create your views here.

def test(request):
    # send_mail_without_celery()
    # send_email_task.delay()
    test_task.delay(10)
    # tidur.delay(60)
    return HttpResponse('<h1>Hello, World!</h1>')