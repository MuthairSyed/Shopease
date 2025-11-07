from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from datetime import timedelta

from .managers import UserManager
from shop.models import Product


class User(AbstractBaseUser):
    email = models.EmailField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)    
    is_admin = models.BooleanField(default=False)  # type: ignore
    is_active = models.BooleanField(default=True)  # type: ignore
    likes = models.ManyToManyField(Product, blank=True, related_name='likes')
    # set a manager role for shop manager to access orders and products
    is_manager = models.BooleanField(default=False)  # type: ignore

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']


    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def get_likes_count(self):
        # Type checking issue with ManyToManyField count() method
        return self.likes.count() if self.likes.exists() else 0  # type: ignore


class Address(models.Model):
    ADDRESS_TYPES = [
        ('home', 'Home'),
        ('office', 'Office'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=50, help_text="e.g. Home, Office, etc.")
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='home')
    full_name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    phone_number = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.full_name}, {self.city}"

    def save(self, *args, **kwargs):
        # If this is the user's first address, make it default
        # Type checking issue with ForeignKey related_name access
        if not self.user.addresses.exists():  # type: ignore
            self.is_default = True
        # If this address is set as default, unset others
        elif self.is_default:
            # Type checking issue with ForeignKey related_name access
            self.user.addresses.exclude(pk=self.pk).update(is_default=False)  # type: ignore
        super().save(*args, **kwargs)

    def get_full_address(self):
        return f"{self.full_name}\n{self.street_address}\n{self.city}, {self.state} {self.postal_code}\n{self.country}\nPhone: {self.phone_number}"


class EmailChangeRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    new_email = models.EmailField()
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'new_email')
    
    def is_expired(self):
        """Check if the email change request has expired (24 hours)"""
        from django.utils.timezone import now
        from datetime import timedelta
        # Add type ignore to bypass static analysis error
        expiration_time = self.created_at + timedelta(hours=24)  # type: ignore
        return now() > expiration_time
    
    def __str__(self):
        return f"Email change request for {self.user.email} to {self.new_email}"  # type: ignore