from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve, reverse
from .models import UserProfile

class EmailVerificationMiddleware:
    """
    Middleware that previously checked for email verification.
    Now allows all users to access any page regardless of email verification status.
    Email verification is now optional and won't restrict page access.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Process the request without any email verification restrictions
        # Email verification is now optional and doesn't affect access
        
        response = self.get_response(request)
        return response 