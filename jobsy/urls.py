from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from core.admin import historical_data_view
from django.contrib.sitemaps.views import sitemap
from core.sitemap import JobSitemap, BlogSitemap, StaticViewSitemap
from django.views.generic.base import TemplateView

# Define the sitemaps dictionary
sitemaps = {
    'jobs': JobSitemap,
    'blog': BlogSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/historical-data/', historical_data_view, name='admin_historical_data'),
    path('i18n/setlanguage/', set_language, name='set_language'),  # Use Django's built-in view with correct path
    path('', include('core.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('ckeditor/', include('ckeditor_uploader.urls')),  # CKEditor 4 URLs
    path('ckeditor5/', include('django_ckeditor_5.urls')),  # CKEditor 5 URLs
    
    # Add sitemap URL
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # Add robots.txt
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
]

urlpatterns += i18n_patterns(
    path('', include('core.urls')),
    prefix_default_language=False,
)

# Only serve media files locally if S3 is disabled and we're in debug mode
if settings.DEBUG and not getattr(settings, 'USE_S3', False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 