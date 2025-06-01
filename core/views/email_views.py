from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from ..models import EmailVerificationToken, UserProfile
import logging

logger = logging.getLogger(__name__)

def send_verification_email(request, user):
    """
    Generate verification token and send verification email to the user
    """
    try:
        # Generate a verification token
        token = EmailVerificationToken.generate_token(user)
        
        # Build verification URL
        verify_url = request.build_absolute_uri(
            reverse('verify_email', kwargs={'token': token.token})
        )
        
        # Prepare email content
        subject = _("Verify your email address")
        html_message = render_to_string('core/email/verify_email.html', {
            'user': user,
            'verify_url': verify_url,
            'expiry_hours': 24,  # Match the expiry time in the token generation
        })
        plain_message = f"""
        {_('Hello')} {user.first_name or user.username},
        
        {_('Thank you for registering with Jobsy. Please verify your email address by clicking the link below:')}
        
        {verify_url}
        
        {_('This link will expire in 24 hours.')}
        
        {_('If you did not register for a Jobsy account, please ignore this email.')}
        
        {_('Best regards,')}
        {_('The Jobsy Team')}
        """
        
        # Send the email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        return False

def verify_email(request, token):
    """
    Handle email verification when user clicks the verification link
    """
    # Get the token or return 404
    token_obj = get_object_or_404(EmailVerificationToken, token=token)
    
    # Check if token is expired
    if not token_obj.is_valid():
        messages.error(request, _("Verification link has expired. Please request a new one."))
        return redirect('login')
    
    # Mark user as verified
    user = token_obj.user
    try:
        user_profile = UserProfile.objects.get(user=user)
        user_profile.is_email_verified = True
        user_profile.save()
        
        # Delete the token as it's been used
        token_obj.delete()
        
        messages.success(request, _("Email verification successful! You can now log in."))
        return redirect('login')
    except Exception as e:
        logger.error(f"Error verifying email: {str(e)}")
        messages.error(request, _("An error occurred during verification. Please try again."))
        return redirect('login')

def resend_verification_email(request):
    """
    Handle resending verification email if user requests it
    """
    if not request.user.is_authenticated:
        messages.error(request, _("You must be logged in to request a verification email."))
        return redirect('login')
    
    user = request.user
    
    # Check if user is already verified
    try:
        user_profile = UserProfile.objects.get(user=user)
        if user_profile.is_email_verified:
            messages.info(request, _("Your email is already verified."))
            return redirect('profile')
    except UserProfile.DoesNotExist:
        messages.error(request, _("User profile not found."))
        return redirect('login')
    
    # Send verification email
    if send_verification_email(request, user):
        messages.success(request, _("Verification email sent. Please check your inbox."))
    else:
        messages.error(request, _("Failed to send verification email. Please try again later."))
    
    return redirect('profile') 