from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import secrets
import string
from datetime import timedelta

class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verification_token')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Verification token for {self.user.username}"
    
    def is_valid(self):
        """Check if the token is still valid (not expired)"""
        return timezone.now() < self.expires_at
    
    @classmethod
    def generate_token(cls, user, expiry_hours=24):
        """
        Generate a new verification token for a user.
        If a token already exists, it will be deleted and a new one created.
        
        Args:
            user: The user to generate a token for
            expiry_hours: Number of hours until the token expires
            
        Returns:
            The generated token string
        """
        # Delete any existing tokens for this user
        cls.objects.filter(user=user).delete()
        
        # Generate a secure random token
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(64))
        
        # Calculate expiration time
        expires_at = timezone.now() + timedelta(hours=expiry_hours)
        
        # Create and save the token
        verification_token = cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        return token
    
    class Meta:
        verbose_name = _("Email Verification Token")
        verbose_name_plural = _("Email Verification Tokens") 