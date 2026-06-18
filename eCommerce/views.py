from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import Product, Order, Order_Item, Store, Product, Review
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import vendor_required, buyer_required
from .models import Product, Store, Review, Cart, Cart_Item
from django.db.models import Avg
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import random
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer
from . import serializers
from .functions.reddit import get_reddit_posts


def reddit_feed(request):
    posts = get_reddit_posts(subreddit="productreview", limit=15)
    return render(request, 'eCommerce/reddit_feed.html', {'posts': posts})


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)  # Only vendor creates store

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        store = self.get_object()
        products = store.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    # or your own logic
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Get product from request data and set user automatically
        product_id = self.request.data.get('product')
        if not product_id:
            raise serializers.ValidationError(
                {"product": "This field is required."})

        serializer.save(
            user=self.request.user,
            product_id=product_id
        )


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


def view_product_page(request):
    user = request.user  # Get the current logged-in user

    # Check if user has permission to view products
    if user.has_perm('eCommerce.view_product') or user.has_perm('eCommerce.view_products'):
        if request.method == 'POST':
            # Get product name from form submission
            product_name = request.POST.get('product')

            if not product_name:
                # If no product name given, show error on page
                return render(request, 'eCommerce/product_page.html', {
                    'error': 'No product name was given.'
                })

            try:
                # Try to find the product in the database by its name
                product = Product.objects.get(name=product_name)
                # Show product details on the page
                return render(request, 'eCommerce/product_page.html', {'product': product})
            except ObjectDoesNotExist:
                # If product not found, show error on page
                return render(request, 'eCommerce/product_page.html', {
                    'error': 'Product not found.'
                })

        # If page is opened normally (GET request), just show empty form
        return render(request, 'eCommerce/product_page.html')

    # If user does not have permission to view products, show error
    return render(request, 'eCommerce/product_page.html', {
        'error': 'You do not have permission to view this product.'
    })


def change_product_price(request):
    user = request.user  # Get the currently logged-in user

    # Check if user has permission to change products
    if user.has_perm('eCommerce.change_product') or user.has_perm('eCommerce.change_products'):
        if request.method == 'POST':
            product_name = request.POST.get(
                'product')  # Get product name from form
            new_price = request.POST.get(
                'new_price')  # Get new price from form

            # Check both fields were filled out
            if not product_name or not new_price:
                return render(request, 'eCommerce/change_price.html', {
                    'error': 'Please provide both product name and new price.'
                })

            try:
                # Find the product in the database
                product = Product.objects.get(name=product_name)

                # Convert new price to float (decimal number)
                product.price = float(new_price)
                product.save()  # Save updated product price to database

                # After success, redirect user to product page
                return HttpResponseRedirect(reverse('eCommerce:product_page'))
            except ValueError:
                # If new price isn't a valid number, show error
                return render(request, 'eCommerce/change_price.html', {
                    'error': 'Invalid price format.'
                })
            except ObjectDoesNotExist:
                # If product name does not exist in database, show error
                return render(request, 'eCommerce/change_price.html', {
                    'error': 'Product not found.'
                })

        # Show form when page is first loaded (GET request)
        return render(request, 'eCommerce/change_price.html')

    # If user does not have permission, show error
    return render(request, 'eCommerce/change_price.html', {
        'error': 'You do not have permission to change prices.'
    })


def list_products(request):
    # Get all products from database
    products = Product.objects.all()
    # Show products list page, passing products to template
    return render(request, 'eCommerce/products_list.html', {'products': products})


@vendor_required
def vendor_dashboard(request):
    stores = request.user.stores.all()
    return render(request, 'eCommerce/vendor/dashboard.html', {'stores': stores})


# CRUD
@vendor_required
def create_store(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        store = Store.objects.create(
            vendor=request.user,
            name=name,
            description=description
        )

        messages.success(request, f"Store '{name}' created successfully!")
        return redirect('eCommerce:vendor_dashboard')

    return render(request, 'eCommerce/vendor/create_store.html')


@vendor_required
def edit_store(request, store_id):
    store = get_object_or_404(Store, id=store_id, vendor=request.user)
    if request.method == 'POST':
        store.name = request.POST.get('name')
        store.description = request.POST.get('description')
        store.save()
        messages.success(request, "Store updated successfully!")
        return redirect('eCommerce:vendor_dashboard')

    return render(request, 'eCommerce/vendor/edit_store.html', {'store': store})


@vendor_required
def delete_store(request, store_id):
    store = get_object_or_404(Store, id=store_id, vendor=request.user)
    store.delete()
    messages.success(request, "Store deleted successfully!")
    return redirect('eCommerce:vendor_dashboard')


#  PRODUCT CRUD
@vendor_required
def add_product(request, store_id):
    store = get_object_or_404(Store, id=store_id, vendor=request.user)

    if request.method == 'POST':
        product = Product.objects.create(
            store=store,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            price=request.POST.get('price'),
            stock=request.POST.get('stock'),
        )
        messages.success(request, f"Product '{product.name}' added!")
        return redirect('eCommerce:vendor_store_products', store_id=store.id)

    return render(request, 'eCommerce/vendor/add_product.html', {'store': store})


@vendor_required
def vendor_store_products(request, store_id):
    store = get_object_or_404(Store, id=store_id, vendor=request.user)
    products = store.products.all()
    return render(request, 'eCommerce/vendor/store_products.html', {
        'store': store,
        'products': products
    })


# @buyer means that the user must be logged in as a buyer
# BUYER ---------------------------------------------------------------------------------------

@buyer_required
def buyer_home(request):
    """Buyer homepage - Featured Products"""

    # Get all active products and pick 3 random ones
    all_products = list(Product.objects.filter(
        is_active=True).select_related('store'))

    if len(all_products) >= 3:
        featured_products = random.sample(all_products, 3)
    else:
        featured_products = all_products  # Show all if less than 3

    # Optional: Get all stores for browsing
    stores = Store.objects.all()

    return render(request, 'eCommerce/buyer/home.html', {
        'featured_products': featured_products,
        'stores': stores,
    })


@buyer_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    reviews = product.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # Check if user has purchased this product
        has_purchased = Order_Item.objects.filter(
            order__buyer=request.user,
            product=product
        ).exists()

        Review.objects.create(
            product=product,
            buyer=request.user,
            rating=rating,
            comment=comment,
            is_verified=has_purchased
        )
        messages.success(request, "Review submitted successfully!")
        return redirect('eCommerce:product_detail', product_id=product.id)

    return render(request, 'eCommerce/buyer/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
    })


@buyer_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Get or create cart
    cart, _ = Cart.objects.get_or_create(buyer=request.user)

    # Get or create cart item
    cart_item, created = Cart_Item.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} added to cart!")
    return redirect('eCommerce:buyer_home')


@buyer_required
def view_cart(request):
    try:
        cart = Cart.objects.get(buyer=request.user)
        cart_items = cart.items.select_related('product').all()

        # Add subtotal for each item
        for item in cart_items:
            item.subtotal = item.product.price * item.quantity   # Add this

        total = sum(item.subtotal for item in cart_items)

    except Cart.DoesNotExist:
        cart_items = []
        total = 0

    return render(request, 'eCommerce/buyer/cart.html', {
        'cart_items': cart_items,
        'total_price': total,
    })


@buyer_required
def remove_from_cart(request, item_id):
    """Remove a specific item from the user's cart"""
    try:
        # Only allow removing items that belong to the current user
        cart_item = Cart_Item.objects.get(
            id=item_id,
            cart__buyer=request.user
        )
        product_name = cart_item.product.name
        cart_item.delete()

        messages.success(
            request, f"{product_name} was removed from your cart.")
    except Cart_Item.DoesNotExist:
        messages.error(request, "Item not found in your cart.")

    return redirect('eCommerce:main_cart_page')


@buyer_required
def checkout(request):
    try:
        cart = Cart.objects.get(buyer=request.user)
        cart_items = cart.items.select_related('product').all()

        if not cart_items:
            messages.error(request, "Your cart is empty!")
            return redirect('eCommerce:main_cart_page')

        total = sum(item.product.price * item.quantity for item in cart_items)

        # Create Order
        order = Order.objects.create(
            buyer=request.user,
            total_amount=total
        )

        # Create Order Items
        for item in cart_items:
            Order_Item.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_time=item.product.price
            )

        # Send Email
        subject = f"Order Confirmation - #{order.id}"
        html_message = render_to_string('eCommerce/buyer/invoice_email.html', {
            'order': order,
            'items': cart_items,
            'total': total,
        })

        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,      # Use configured email
            to=[request.user.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)

        # Clear Cart
        cart.items.all().delete()

        messages.success(
            request,
            f"Checkout successful! Receipt sent to <strong>{request.user.email}</strong>"
        )
        return redirect('eCommerce:buyer_home')

    except Cart.DoesNotExist:
        messages.error(request, "Cart not found.")
        return redirect('eCommerce:buyer_home')
    except Exception as e:
        messages.error(request, f"Checkout failed: {e}")
        return redirect('eCommerce:main_cart_page')


@buyer_required
def product_catalog(request):
    """Full product catalog with search"""
    query = request.GET.get('q', '')  # Get search term from URL

    products = Product.objects.filter(is_active=True).select_related(
        'store').order_by('-created_at')

    if query:
        # Search by name (case-insensitive)
        products = products.filter(name__icontains=query)

    return render(request, 'eCommerce/buyer/catalog.html', {
        'products': products,
        'query': query,   # Pass search term back to template
    })


@buyer_required
def store_detail(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    products = store.products.filter(is_active=True).order_by('name')

    return render(request, 'eCommerce/buyer/store_detail.html', {
        'store': store,
        'products': products,
    })
