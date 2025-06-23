from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from core.models.base import SoftDeletionModel

# Import storage backends if S3 is enabled
if hasattr(settings, 'USE_S3') and settings.USE_S3:
    from jobsy.storage_backends import PublicMediaStorage, PrivateMediaStorage
else:
    PublicMediaStorage = None
    PrivateMediaStorage = None

class BlogPost(SoftDeletionModel):
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_("სათაური"))
    slug = models.SlugField(max_length=250, unique=True, verbose_name=_("სლაგი"))
    content = CKEditor5Field(verbose_name=_("კონტენტი"))
    excerpt = models.TextField(max_length=500, blank=True, verbose_name=_("მოკლე აღწერა"))
    meta_description = models.CharField(max_length=160, blank=True, verbose_name=_("მეტა აღწერა"))
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name=_("მეტა საკვანძო სიტყვები"))
    
    # Use PublicMediaStorage for featured images when S3 is enabled
    if PublicMediaStorage:
        featured_image = models.ImageField(
            upload_to='blog_images/', 
            storage=PublicMediaStorage(),
            blank=True, 
            null=True, 
            verbose_name=_("მთავარი სურათი")
        )
    else:
        featured_image = models.ImageField(
            upload_to='blog_images/', 
            blank=True, 
            null=True, 
            verbose_name=_("მთავარი სურათი")
        )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='blog_posts',
        verbose_name=_("ავტორი")
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_("სტატუსი")
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("შექმნის თარიღი"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("განახლების თარიღი"))
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("გამოქვეყნების თარიღი"))
    
    # SEO and social sharing fields
    allow_comments = models.BooleanField(default=True, verbose_name=_("კომენტარების დაშვება"))
    view_count = models.PositiveIntegerField(default=0, verbose_name=_("ნახვების რაოდენობა"))
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = _("ბლოგის პოსტი")
        verbose_name_plural = _("ბლოგის პოსტები")
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['status']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
            
            # Check if the slug already exists and make it unique if needed
            original_slug = self.slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog_post_detail', kwargs={'slug': self.slug})
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


class BlogCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("კატეგორიის სახელი"))
    slug = models.SlugField(max_length=120, unique=True, verbose_name=_("სლაგი"))
    description = models.TextField(blank=True, verbose_name=_("აღწერა"))
    
    class Meta:
        verbose_name = _("ბლოგის კატეგორია")
        verbose_name_plural = _("ბლოგის კატეგორიები")
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog_category', kwargs={'slug': self.slug})


class BlogPostCategory(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='posts')
    
    class Meta:
        verbose_name = _("პოსტის კატეგორია")
        verbose_name_plural = _("პოსტების კატეგორიები")
        unique_together = ('post', 'category')
    
    def __str__(self):
        return f"{self.post.title} - {self.category.name}"


class BlogTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("ტეგის სახელი"))
    slug = models.SlugField(max_length=70, unique=True, verbose_name=_("სლაგი"))
    
    class Meta:
        verbose_name = _("ბლოგის ტეგი")
        verbose_name_plural = _("ბლოგის ტეგები")
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog_tag', kwargs={'slug': self.slug}) 