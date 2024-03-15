from celery import shared_task
import time
from django.core.mail import send_mail

@shared_task
def tidur(duration):
    time.sleep(duration)
    return duration

@shared_task
def send_email_task():
    send_mail('Ini adalah tugas dari Celery!', 
              'Email ini berhasil dikirim oleh Celery!',
              'tribberyoni5@gmail.com',
              ['tribberyoni5@gmail.com','tribberyoni6@gmail.com',
               'tribberyoni4@gmail.com', 'yoni.tribber.ti.20@cic.ac.id'],
                fail_silently=False
    )
    print('Email berhasil dikirim dari Celery Worker!')
    return 'Email berhasil dikirim dari Celery Worker!'

@shared_task
def add(x, y):
    return x + y

@shared_task
def test_task(number):
    n = number + 1
    for i in range(number):
        n -= 1
        if n % 10 == 0:
            print(n)
        # print(n)
        time.sleep(1)
    return "Test task done!"