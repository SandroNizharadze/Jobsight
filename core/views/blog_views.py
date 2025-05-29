from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Count
from django.utils import timezone
from core.models import BlogPost, BlogCategory, BlogTag, BlogPostCategory
from django.http import Http404

class BlogListView(ListView):
    model = BlogPost
    template_name = 'core/blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Return published blog posts only"""
        return BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('author')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.annotate(
            post_count=Count('posts__post', distinct=True)
        ).order_by('-post_count')[:10]
        
        # Fixed query for popular tags
        context['popular_tags'] = BlogTag.objects.annotate(
            post_count=Count('id')
        ).order_by('-post_count')[:15]
        
        context['recent_posts'] = BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).order_by('-published_at')[:5]
        
        # SEO metadata
        context['meta_title'] = 'Jobsy ბლოგი - კარიერული რჩევები და სიახლეები'
        context['meta_description'] = 'გაეცანით უახლეს სტატიებს დასაქმების, კარიერული განვითარების და პროფესიული ზრდის შესახებ Jobsy-ს ბლოგზე.'
        context['meta_keywords'] = 'ბლოგი, კარიერა, დასაქმება, სამსახური, პროფესიული განვითარება'
        
        return context

class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'core/blog/blog_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        """Only show published posts to regular users"""
        if self.request.user.is_staff:
            return BlogPost.objects.all()
        return BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Increment view count
        post.increment_view_count()
        
        # Get categories for this post
        post_categories = BlogPostCategory.objects.filter(
            post=post
        ).values_list('category_id', flat=True)
        
        # Get related posts based on categories
        context['related_posts'] = BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now(),
            categories__category_id__in=post_categories
        ).exclude(id=post.id).distinct().order_by('-published_at')[:3]
        
        # Get categories for sidebar
        context['categories'] = BlogCategory.objects.annotate(
            post_count=Count('posts__post', distinct=True)
        ).order_by('-post_count')[:10]
        
        # Fixed query for popular tags
        context['popular_tags'] = BlogTag.objects.annotate(
            post_count=Count('id')
        ).order_by('-post_count')[:15]
        
        # SEO metadata
        context['meta_title'] = post.title
        context['meta_description'] = post.meta_description or post.excerpt or f"{post.title} - Jobsy ბლოგი"
        context['meta_keywords'] = post.meta_keywords
        
        return context
    
    def get_object(self, queryset=None):
        """Override to handle 404 for unpublished posts"""
        try:
            obj = super().get_object(queryset)
            return obj
        except Http404:
            raise Http404("ბლოგის პოსტი არ მოიძებნა")

class BlogCategoryView(ListView):
    model = BlogPost
    template_name = 'core/blog/blog_category.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        self.category = get_object_or_404(BlogCategory, slug=self.kwargs['slug'])
        return BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now(),
            categories__category=self.category
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        
        # Get categories for sidebar
        context['categories'] = BlogCategory.objects.annotate(
            post_count=Count('posts__post', distinct=True)
        ).order_by('-post_count')[:10]
        
        # Fixed query for popular tags
        context['popular_tags'] = BlogTag.objects.annotate(
            post_count=Count('id')
        ).order_by('-post_count')[:15]
        
        # SEO metadata
        context['meta_title'] = f"{self.category.name} - Jobsy ბლოგი"
        context['meta_description'] = self.category.description or f"სტატიები კატეგორიაში {self.category.name} - Jobsy ბლოგი"
        context['meta_keywords'] = f"{self.category.name}, ბლოგი, კარიერა, დასაქმება"
        
        return context

class BlogTagView(ListView):
    model = BlogPost
    template_name = 'core/blog/blog_tag.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        self.tag = get_object_or_404(BlogTag, slug=self.kwargs['slug'])
        return BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now(),
            categories__category__posts__post__tags=self.tag
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        
        # Get categories for sidebar
        context['categories'] = BlogCategory.objects.annotate(
            post_count=Count('posts__post', distinct=True)
        ).order_by('-post_count')[:10]
        
        # Fixed query for popular tags
        context['popular_tags'] = BlogTag.objects.annotate(
            post_count=Count('id')
        ).order_by('-post_count')[:15]
        
        # SEO metadata
        context['meta_title'] = f"#{self.tag.name} - Jobsy ბლოგი"
        context['meta_description'] = f"სტატიები ტეგით #{self.tag.name} - Jobsy ბლოგი"
        context['meta_keywords'] = f"{self.tag.name}, ბლოგი, კარიერა, დასაქმება"
        
        return context 