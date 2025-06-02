from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import JobListing, BlogPost
from django.utils import timezone
from datetime import timedelta

class JobSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        # Only include active jobs
        return JobListing.objects.filter(status='approved', deleted_at=None)

    def lastmod(self, obj):
        return obj.updated_at or obj.posted_at

    def location(self, obj):
        return reverse('job_detail', args=[obj.id])


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return BlogPost.objects.filter(status='published', deleted_at=None)

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at

    def location(self, obj):
        return reverse('blog_post_detail', args=[obj.slug])


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ['job_list', 'login', 'register', 'blog_list', 'pricing']

    def location(self, item):
        return reverse(item) 