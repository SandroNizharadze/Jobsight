from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve, reverse
from .models import UserProfile

class EmailVerificationMiddleware:
    """
    Middleware to check if a user's email is verified before allowing access to certain pages.
    If the email is not verified, the user is redirected to a page with instructions.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Process the request
        if request.user.is_authenticated:
            # Get current URL name
            current_url = resolve(request.path_info).url_name
            
            # List of URLs that don't require email verification
            exempt_urls = [
                'verify_email', 
                'resend_verification', 
                'logout', 
                'login', 
                'register',
                'profile',  # Allow access to profile to see verification status
            ]
            
            # Check if the current URL requires email verification
            if current_url not in exempt_urls:
                try:
                    user_profile = UserProfile.objects.get(user=request.user)
                    if not user_profile.is_email_verified:
                        # If the user is an admin, bypass the verification
                        if request.user.is_superuser or user_profile.role == 'admin':
                            return self.get_response(request)
                            
                        messages.warning(
                            request, 
                            "Please verify your email address to access this page. "
                            "Check your inbox for the verification link or visit your profile to resend it."
                        )
                        return redirect('profile')
                except UserProfile.DoesNotExist:
                    # If profile doesn't exist, let the request continue
                    # This will be handled elsewhere
                    pass
        
        response = self.get_response(request)
        return response 