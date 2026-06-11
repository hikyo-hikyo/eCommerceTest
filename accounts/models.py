
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('vendor', 'Vendor'),
    )
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='buyer')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_vendor(self):
        return self.role == 'vendor'

    @property
    def is_buyer(self):
        return self.role == 'buyer'
