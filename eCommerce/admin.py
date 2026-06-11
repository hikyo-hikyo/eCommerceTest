from django.contrib import admin
from .models import Product, Review, Cart, Cart_Item

# Register your models here.
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(Cart_Item)
