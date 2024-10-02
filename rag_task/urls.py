from django.conf import settings
from django.urls import path
from . import views, wa_webhook, telegram_api
from django.conf.urls.static import static

urlpatterns = [
    path('api/v1/chat/', view=views.chat, name='chat'),
    path('webhook/', view=wa_webhook.webhook, name='webhook'),
    path('home/', view=wa_webhook.home, name='home'),
    path('reset/', view=wa_webhook.reset, name='reset'),
    path('getpost/', view=telegram_api.telegram_bot, name='telegram_bot'),
    path('setwebhook/', view=telegram_api.setwebhook, name='setwebhook'),
]

# Tambahkan URL untuk menyajikan file media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)