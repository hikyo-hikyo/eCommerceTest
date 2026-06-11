from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('vendor', 'Vendor'),
    )
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='buyer')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)


class Product(models.Model):
    name = models.CharField(max_length=100)
    # The name of the product, like "T-shirt" or "Laptop"

    description = models.TextField(blank=True)
    # A longer description of the product; it’s optional (can be empty)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    # The price of the product, with up to 10 digits total and 2 decimal places for cents

    stock = models.PositiveIntegerField()
    # How many items are available in stock (only positive numbers allowed)

    def __str__(self):
        # This makes it easier to see the product’s name when printing or in admin pages
        return self.name

    class Meta:
        # These are special permissions for users who can add, change, delete, or view products
        permissions = [
            ("add_products", "Can add products"),
            ("change_products", "Can change products"),
            ("delete_products", "Can delete products"),
            ("view_products", "Can view products"),
        ]


class Store(models.Model):
    vendor = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, limit_choices_to={'role': 'vendor'})
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='store_logos/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
