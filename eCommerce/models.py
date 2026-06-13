from django.db import models
from accounts.models import User


class Product(models.Model):
    store = models.ForeignKey(
        'Store', on_delete=models.CASCADE, related_name='products')

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Store(models.Model):
    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stores'      # This must be 'stores'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer.username} - {self.product.name} ({self.rating}★)"


class Cart(models.Model):
    buyer = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.buyer.username}"


class Cart_Item(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')   # Prevent duplicate items

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Order(models.Model):
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=True)

    def __str__(self):
        return f"Order #{self.id} - {self.buyer.username}"


class Order_Item(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_time = models.DecimalField(
        max_digits=10, decimal_places=2)  # Save price at purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
