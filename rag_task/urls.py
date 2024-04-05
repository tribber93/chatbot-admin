from django.conf import settings
from django.urls import path
from . import views, webhook
from django.conf.urls.static import static

urlpatterns = [
    # path('ingest/', view=views.result, name='ingest'),
    # path('ingest/test', view=views.test, name='test'),
    path('chat/', view=views.chat, name='chat'),
    path('yt93/webhook', view=webhook.webhook, name='webhook'),
    path('home/', view=webhook.home, name='home'),
    path('reset/', view=webhook.reset, name='reset'),
]

# Tambahkan URL untuk menyajikan file media
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)