import os
from django.core.management.base import BaseCommand
from django.utils import timezone
import xml.dom.minidom

class Command(BaseCommand):
    help = 'Generate sitemap.xml file'

    def handle(self, *args, **options):
        self.stdout.write('Generating sitemap.xml...')
        
        # Define the domain
        domain = 'jobsight.ge'
        
        # Define static URLs
        static_urls = [
            '/',
            '/jobs/',
            '/about/',
            '/contact/',
            '/terms/',
            '/privacy/',
            '/blog/',
        ]
        
        # Generate sitemap
        sitemap_urls = []
        
        # Add static URLs
        for url in static_urls:
            sitemap_urls.append({
                'loc': f"https://{domain}{url}",
                'lastmod': timezone.now().strftime('%Y-%m-%dT%H:%M:%S%z'),
                'changefreq': 'weekly',
                'priority': '0.8'
            })
        
        # Create XML document
        doc = xml.dom.minidom.getDOMImplementation().createDocument(None, 'urlset', None)
        root = doc.documentElement
        root.setAttribute('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        # Add URLs to sitemap
        for url_info in sitemap_urls:
            url_element = doc.createElement('url')
            
            loc_element = doc.createElement('loc')
            loc_text = doc.createTextNode(url_info['loc'])
            loc_element.appendChild(loc_text)
            url_element.appendChild(loc_element)
            
            lastmod_element = doc.createElement('lastmod')
            lastmod_text = doc.createTextNode(url_info['lastmod'])
            lastmod_element.appendChild(lastmod_text)
            url_element.appendChild(lastmod_element)
            
            changefreq_element = doc.createElement('changefreq')
            changefreq_text = doc.createTextNode(url_info['changefreq'])
            changefreq_element.appendChild(changefreq_text)
            url_element.appendChild(changefreq_element)
            
            priority_element = doc.createElement('priority')
            priority_text = doc.createTextNode(url_info['priority'])
            priority_element.appendChild(priority_text)
            url_element.appendChild(priority_element)
            
            root.appendChild(url_element)
        
        # Make sure static directory exists
        os.makedirs('static', exist_ok=True)
        
        # Save to file
        sitemap_path = os.path.join('static', 'sitemap.xml')
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(doc.toprettyxml(indent='  '))
        
        self.stdout.write(self.style.SUCCESS(f'Sitemap generated successfully at {sitemap_path}')) 