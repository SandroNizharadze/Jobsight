from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve, reverse
from .models import UserProfile
import logging
from django.http import HttpRequest

# Set up logger
logger = logging.getLogger(__name__)

class EmailVerificationMiddleware:
    """
    Middleware that previously checked for email verification.
    Now allows all users to access any page regardless of email verification status.
    Email verification is now optional and won't restrict page access.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Log request information for debugging
        logger.info(f"Request HOST: {request.get_host()}")
        logger.info(f"Request META HTTP_HOST: {request.META.get('HTTP_HOST', 'NO_HTTP_HOST')}")
        
        # Process the request without any email verification restrictions
        # Email verification is now optional and doesn't affect access
        
        response = self.get_response(request)
        return response

class FixHostHeaderMiddleware:
    """
    Middleware to handle the domain transition from jobsy.ge to jobsight.ge
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request: HttpRequest):
        # Check if we're getting requests to jobsight.ge
        host = request.META.get('HTTP_HOST', '')
        logger.info(f"FixHostHeaderMiddleware received host: {host}")
        
        # If the host is jobsight.ge or www.jobsight.ge, ensure it's accepted
        if host in ['jobsight.ge', 'www.jobsight.ge']:
            # Save the original host
            original_host = host
            logger.info(f"Fixing host header for {original_host}")
            
            # Process the request
            try:
                response = self.get_response(request)
                logger.info(f"Successfully processed request for {original_host}")
                return response
            except Exception as e:
                logger.error(f"Error processing request for {original_host}: {str(e)}")
                # If there's an error, modify the allowed hosts directly
                from django.conf import settings
                if original_host not in settings.ALLOWED_HOSTS:
                    logger.info(f"Adding {original_host} to ALLOWED_HOSTS")
                    settings.ALLOWED_HOSTS.append(original_host)
                    # Try again
                    return self.get_response(request)
                raise
        else:
            # For other hosts, proceed normally
            return self.get_response(request) 