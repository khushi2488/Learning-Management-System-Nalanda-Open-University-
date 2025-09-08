from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from nouapp.views import set_theme

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('nouapp.nouappurls', 'nouapp'), namespace='nouapp')),
    path('studentapp/', include(('studentapp.studentappurls', 'studentapp'), namespace='studentapp')),
    path('adminapp/', include(('adminapp.adminappurls', 'adminapp'), namespace='adminapp')),
    path('set-theme/', set_theme, name='set-theme'),
]

# ✅ Serve static & media in development (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
