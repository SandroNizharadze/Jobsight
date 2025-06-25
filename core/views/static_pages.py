from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from core.models import StaticPage
from django.utils.translation import gettext_lazy as _

class StaticPageView(DetailView):
    model = StaticPage
    template_name = 'core/static_page.html'
    context_object_name = 'page'
    
    def get_object(self, queryset=None):
        page_type = self.kwargs.get('page_type')
        return get_object_or_404(StaticPage, page_type=page_type)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        return context 