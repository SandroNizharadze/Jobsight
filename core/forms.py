from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, EmployerProfile, JobListing
from django.contrib.auth.forms import UserCreationForm
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.widgets import CKEditor5Widget
import re

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=False)
    # Define role as a separate field - not a model field
    role = forms.ChoiceField(
        choices=[('candidate', _('სამუშაოს მაძიებელი')), ('employer', _('დამსაქმებელი'))],
        widget=forms.RadioSelect,
        initial='candidate',
        required=True
    )
    # Add checkbox for email notifications
    email_notifications = forms.BooleanField(
        label=_('I agree to receive email notifications about news'),
        required=False,  # Make it optional
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    # Add checkbox for terms and conditions
    terms_agreement = forms.BooleanField(
        label=_('I agree to the Terms & Conditions and Privacy Policy'),
        required=True,
        error_messages={
            'required': _('You must agree to the Terms & Conditions and Privacy Policy to register.')
        },
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'email_notifications', 'terms_agreement']
        widgets = {
            'username': forms.HiddenInput(),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Email')}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Name')}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username field hidden and populate it with email value
        self.fields['username'].required = False
        # Keep password2 field but no need for help text
        self.fields['password2'].help_text = None
        # Remove password validation messages
        self.fields['password1'].help_text = None
        self.fields['password1'].error_messages = {
            'required': _('Please enter your password.'),
        }
        # Make role field more prominent
        self.fields['role'].widget.attrs.update({'class': 'form-check-input'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("A user with that email already exists."))
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError(_("A user with that email already exists."))
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 4:
            raise forms.ValidationError(_("Password must be at least 4 characters long."))
        return password

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if email:
            # Set username to be the same as email
            cleaned_data['username'] = email
        
        # Explicitly capture role for later use in the view
        role = cleaned_data.get('role')
        if role not in ['candidate', 'employer']:
            # Default to candidate if invalid value
            cleaned_data['role'] = 'candidate'
        
        return cleaned_data

class EmployerRegistrationForm(forms.ModelForm):
    """Form for employer-specific registration information"""
    company_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Company Name')})
    )
    company_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Identification Code')})
    )
    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Mobile Number')})
    )
    
    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'company_id', 'phone_number']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add company_id and phone_number to EmployerProfile temporarily for registration
        self.fields['company_id'] = forms.CharField(required=False)
        self.fields['phone_number'] = forms.CharField(required=True)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture', 
            'cv', 
            'desired_field', 
            'field_experience', 
            'visible_to_employers',
            'phone_number'
        ]
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'cv': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'desired_field': forms.Select(attrs={
                'class': 'form-control'
            }),
            'field_experience': forms.Select(attrs={
                'class': 'form-control'
            }),
            'visible_to_employers': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your phone number')
            }),
        }
        help_texts = {
            'cv': 'Upload your CV (PDF, DOC, DOCX).',
            'visible_to_employers': 'Allow employers to view your CV in the database.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set choices for desired_field from JobListing.CATEGORY_CHOICES
        self.fields['desired_field'].choices = [('', '----------')] + list(JobListing.CATEGORY_CHOICES)
        # Set choices for field_experience from JobListing.EXPERIENCE_CHOICES
        self.fields['field_experience'].choices = [('', '----------')] + list(JobListing.EXPERIENCE_CHOICES)
        
        # If no CV is uploaded, set visible_to_employers to False
        instance = kwargs.get('instance')
        if instance and not instance.cv:
            self.fields['visible_to_employers'].initial = False
            self.fields['visible_to_employers'].disabled = True

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        # Only validate if a new file is being uploaded
        if profile_picture and isinstance(profile_picture, UploadedFile):
            if profile_picture.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file too large ( > 5MB )")
            if not profile_picture.content_type.startswith('image/'):
                raise forms.ValidationError("File is not an image")
        return profile_picture
        
    def clean_visible_to_employers(self):
        """Handle string values for visible_to_employers from toggle button"""
        value = self.cleaned_data.get('visible_to_employers')
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'on')
        return bool(value)

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Ensure visible_to_employers is False when no CV is uploaded
        if not instance.cv:
            instance.visible_to_employers = False
        
        if commit:
            instance.save()
        return instance

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ('company_name', 'company_id', 'phone_number', 'show_phone_number', 'company_website', 'company_description', 'company_logo',
                 'company_size', 'industry', 'location')
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your company name'
            }),
            'company_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter identification code')
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter phone number')
            }),
            'company_website': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.example.com'
            }),
            'company_description': CKEditor5Widget(
                attrs={'class': 'django_ckeditor_5'}, 
                config_name='default'
            ),
            'company_logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'company_size': forms.Select(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g., Technology, Healthcare, Finance'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            }),
        }

    def clean_company_logo(self):
        company_logo = self.cleaned_data.get('company_logo')
        # Only validate if a new file is being uploaded
        if company_logo and isinstance(company_logo, UploadedFile):
            if company_logo.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file too large ( > 5MB )")
            if not company_logo.content_type.startswith('image/'):
                raise forms.ValidationError("File is not an image")
        return company_logo

    def clean_company_description(self):
        """Ensure proper handling of Georgian characters in company description"""
        data = self.cleaned_data.get('company_description', '')
        
        # If data is empty, return it as is
        if not data or data.strip() == '':
            return data
        
        # No special processing needed for regular textarea
        # Just ensure it's a proper string
        return str(data)

class JobListingForm(forms.ModelForm):
    # Add georgian_language_only as a form field (not a model field)
    georgian_language_only = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.RadioSelect(choices=[(True, 'კი'), (False, 'არა')]),
    )
    use_external_link = forms.BooleanField(
        required=False,
        label=_('ვაკანსია ატვირთულია გარე ლინკით'),
        help_text=_('მონიშნეთ თუ გსურთ კანდიდატები გადამისამართდნენ გარე ვებ-გვერდზე.'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    external_link = forms.URLField(
        required=False,
        label=_('External Link'),
        help_text=_('ჩასვით ვაკანსიის გარე ბმული.'),
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'})
    )
    
    class Meta:
        model = JobListing
        fields = (
            'title', 'description', 'location', 'salary_min', 'salary_max', 'salary_type',
            'category', 'experience', 'job_preferences', 'considers_students', 'premium_level',
            'georgian_language_only', 'use_external_link', 'external_link'
        )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}),
            'description': CKEditor5Widget(
                attrs={'class': 'django_ckeditor_5'}, 
                config_name='default'
            ),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minimum Salary'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Maximum Salary'}),
            'salary_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'experience': forms.Select(attrs={'class': 'form-control'}),
            'job_preferences': forms.Select(attrs={'class': 'form-control'}),
            'considers_students': forms.RadioSelect(attrs={'class': 'btn-check'}),
            'premium_level': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize the georgian_language_only field with the model instance value if editing
        if self.instance and self.instance.pk:
            self.fields['georgian_language_only'].initial = self.instance.georgian_language_only
        
        # Add btn-check class to the radio buttons
        self.fields['georgian_language_only'].widget.attrs.update({'class': 'btn-check'})
        
        # Make premium_level not required in the form validation
        self.fields['premium_level'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        # Ensure georgian_language_only is never None/NULL
        if 'georgian_language_only' not in cleaned_data or cleaned_data['georgian_language_only'] is None:
            cleaned_data['georgian_language_only'] = False
        if cleaned_data.get('use_external_link') and not cleaned_data.get('external_link'):
            self.add_error('external_link', _('გთხოვთ ჩასვათ გარე ბმული'))
            
        # Validate premium_level
        premium_level = cleaned_data.get('premium_level')
        if not premium_level or premium_level not in ['standard', 'premium', 'premium_plus']:
            # Default to standard if not provided or invalid
            cleaned_data['premium_level'] = 'standard'
            
        return cleaned_data