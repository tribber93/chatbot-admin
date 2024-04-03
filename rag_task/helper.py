from django.core.mail import send_mail

def send_mail_without_celery():  
    send_mail('Email tanpa Celery!', 
              'Ini bukanlah email dari Celery!',
              'tribberyoni5@gmail.com',
              ['tribberyoni6@gmail.com'],
                fail_silently=False
    )
    return 'Email berhasil dikirim! tanpa menggunakan Celery Worker!'