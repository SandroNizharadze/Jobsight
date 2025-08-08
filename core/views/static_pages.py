from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render

class StaticPageView(TemplateView):
    template_name = 'core/static_page.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_type = self.kwargs.get('page_type')
        
        if page_type == 'privacy_policy':
            context['title'] = _('Privacy Policy')
            context['page_type'] = 'privacy_policy'
        elif page_type == 'terms_conditions':
            context['title'] = _('Terms and Conditions')
            context['page_type'] = 'terms_conditions'
        
        return context

def language_demo(request):
    """View function for the language demo page."""
    return render(request, 'core/language_demo.html') 