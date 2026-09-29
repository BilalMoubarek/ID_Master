from django.contrib import admin
from django.urls import path, include
from accounts.views import home_view
from django.conf import settings
from django.conf.urls.static import static
from lms.views import api_overview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('', include('accounts.urls')),
    path('lms/', include('lms.urls')),
    path('api/', api_overview, name='api-overview'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)