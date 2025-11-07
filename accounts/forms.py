from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings

from accounts.models import User, Address


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter email address'}
        )
    )
    full_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter full name'}
        )
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'full_name', 'password1', 'password2')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter email address'}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter password'}
        )
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if it's a valid email format
            if '@' not in email or '.' not in email.split('@')[-1]:
                raise ValidationError("Please enter a valid email address.")
        return email


class ManagerLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter manager email'}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter password'}
        )
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if it's a valid email format
            if '@' not in email or '.' not in email.split('@')[-1]:
                raise ValidationError("Please enter a valid email address.")
        return email


class EditProfileForm(forms.ModelForm):
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter current password'}
        ),
        required=False
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter new password'}
        ),
        required=False
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}
        ),
        required=False
    )
    
    class Meta:
        model = User
        fields = ['full_name', 'email']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Store original email for comparison
        self.original_email = self.instance.email
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email is being changed
        if email != self.original_email:
            # Check if the new email is already taken by another user
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise ValidationError("This email address is already registered. Please try a different email address.")
        return email
        
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if old_password and not self.user.check_password(old_password):
            raise ValidationError("Your current password is incorrect.")
        return old_password
        
    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError("The two password fields didn't match.")
        if new_password2:
            password_validation.validate_password(new_password2, self.user)
        return new_password2
        
    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if (new_password1 or new_password2) and not old_password:
            raise ValidationError("Please enter your current password to change your password.")
            
        if old_password and not (new_password1 and new_password2):
            raise ValidationError("Please enter both new password fields to change your password.")
            
        return cleaned_data
        
    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password2')
        new_email = self.cleaned_data.get('email')
        
        # Check if email is being changed
        if new_email and new_email != self.original_email:
            # Don't save the new email yet, but store it for verification
            # We'll handle email verification in the view
            if commit:
                # Save other fields except email
                # Only save full_name if it has changed
                if hasattr(self, 'changed_data') and 'full_name' in getattr(self, 'changed_data', []):
                    user.save(update_fields=['full_name'])
                # Return the user without saving to prevent email change
                return user
        else:
            # Email is not being changed, proceed normally
            if new_password:
                user.set_password(new_password)
            if commit:
                user.save()
        return user


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['title', 'address_type', 'full_name', 'street_address', 'city', 'state', 'postal_code', 'country', 'phone_number', 'is_default']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Home, Office'}),
            'address_type': forms.Select(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['country'].initial = 'India'

    def save(self, commit=True):
        address = super().save(commit=False)
        address.user = self.user
        if commit:
            address.save()
        return address