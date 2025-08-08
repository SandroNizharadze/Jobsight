from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.admin import historical_data_view
from django.contrib.sitemaps.views import sitemap
from core.sitemap import JobListingSitemap, BlogSitemap, StaticViewSitemap
from django_ckeditor_5.views import upload_file
from django.views.generic.base import TemplateView
from django.views.static import serve
import os

# Define the sitemaps dictionary
sitemaps = {
    'jobs': JobListingSitemap,
    'blog': BlogSitemap,
    'static': StaticViewSitemap,
}

# Custom view to serve static sitemap or fall back to dynamic sitemap
def serve_sitemap(request):
    static_sitemap_path = os.path.join(settings.BASE_DIR, 'static', 'sitemap.xml')
    if os.path.exists(static_sitemap_path):
        return serve(request, 'sitemap.xml', document_root=os.path.join(settings.BASE_DIR, 'static'))
    else:
        return sitemap(request, {'sitemaps': sitemaps})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/historical-data/', historical_data_view, name='admin_historical_data'),
    path('', include('core.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    
    # CKEditor URLs
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('ckeditor5/upload/', upload_file, name='ck_editor_5_upload_file'),
    
    # Add sitemap URL - will serve static file if it exists, otherwise use dynamic sitemap
    path('sitemap.xml', serve_sitemap, name='sitemap'),
    
    # Add robots.txt
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

# Only serve media files locally if S3 is disabled and we're in debug mode
if settings.DEBUG and not getattr(settings, 'USE_S3', False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 