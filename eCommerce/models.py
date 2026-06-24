from django.db import models
from django.conf import settings
from accounts.models import User
from django.contrib.auth import get_user_model


User = get_user_model()


class Store(models.Model):
    """Store model is owned by one user and can contain many products."""
    vendor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='stores')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (by {self.vendor.username})"


class Product(models.Model):
    """Product model is owned by one store and can have many reviews associated with it."""
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Review(models.Model):
    """Review model is owned by one user and can be associated with one product."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Verified" if self.is_verified else "Unverified"
        return f"{self.buyer.username} - {self.product.name} ({status})"


class Cart(models.Model):
    """Cart model is owned by one user and can have many items in the cart."""
    buyer = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.buyer.username}"


class Cart_Item(models.Model):
    """Cart item model is owned by one cart. Prevents duplicate items displaying in the cart. Instead it will update the quantity."""
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')   # Prevent duplicate items

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    """Completed or placed order by a buyer. Summary of all items in the order."""
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=True)

    def __str__(self):
        return f"Order #{self.id} - {self.buyer.username}"


class Order_Item(models.Model):
    """These are the individual items in an order."""
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_time = models.DecimalField(
        max_digits=10, decimal_places=2)  # Save price at purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
