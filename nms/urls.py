
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('numman.urls')),
    path('',include('users.urls')),
    path('',include('oper.urls')),
    path('',include('api.urls')),
    path('',include('groups.urls')),
    path('', include('audio_manager.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)