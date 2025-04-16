from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('accounts/', include('allauth.urls')), 
    path('accounts/', include('apps.accounts.urls')),  
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('solutions/', include('apps.solutions.urls')),
    path('blog/', include('apps.blog.urls')),
    path('api/', include('apps.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]