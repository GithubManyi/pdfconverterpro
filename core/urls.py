"""Main URL configuration."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from health import health_check 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('tools/', include('converter.urls')),
    path('healthz/', health_check),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler404 = 'home.views.handler_404'
handler500 = 'home.views.handler_500'


