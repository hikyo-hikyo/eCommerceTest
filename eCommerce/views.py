from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import Product
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Store, Product
from accounts.decorators import vendor_required
from accounts.decorators import buyer_required
from .models import Product, Store, Review, Cart, Cart_Item
from django.db.models import Avg


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


def add_item_to_cart(request):
    # Get item name and quantity from POST form submission
    item = request.POST.get('item')
    quantity = request.POST.get('quantity')

    # If either is missing, redirect to cart page without changing anything
    if not item or not quantity:
        return redirect('eCommerce:main_cart_page')

    try:
        # Convert quantity to integer, and set to 1 if invalid or less than 1
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    # Get existing cart from session, or empty dictionary if none
    cart = request.session.get('cart', {})

    # If item already in cart, add to existing quantity, otherwise add new item
    if item in cart:
        cart[item] += quantity
    else:
        cart[item] = quantity

    # Save updated cart back into session so it persists
    request.session['cart'] = cart
    request.session.modified = True  # Mark session as changed

    # Redirect user to cart page after adding item
    return redirect(reverse('eCommerce:main_cart_page'))


def retrieve_products(request):
    products = []
    session = request.session

    # If cart exists in session, load products and their quantities
    if 'cart' in session:
        for name, quantity in session['cart'].items():
            try:
                # Get product from database by name
                product = Product.objects.get(name=name)
                # Add product and quantity as a dictionary to list
                products.append({'product': product, 'quantity': quantity})
            except Product.DoesNotExist:
                # Skip if product not found (may have been deleted)
                pass

    return products


def show_user_cart(request):
    # Get list of products and quantities from the session cart
    cart_items = retrieve_products(request)

    total_price = 0  # Start total price at zero

    # Calculate subtotal for each cart item and total price for whole cart
    for item in cart_items:
        subtotal = item['product'].price * item['quantity']
        item['subtotal'] = subtotal  # Add subtotal to item dictionary
        total_price += subtotal

    # Render cart page, passing in items and total price
    return render(request, 'eCommerce/main_cart_page.html', {
        'cart': cart_items,
        'total_price': total_price,
    })


def list_products(request):
    # Get all products from database
    products = Product.objects.all()
    # Show products list page, passing products to template
    return render(request, 'eCommerce/products_list.html', {'products': products})


def clear_cart(request):
    # Empty the cart by setting session cart to empty dictionary
    request.session['cart'] = {}
    request.session.modified = True  # Mark session as changed

    # Redirect to cart page after clearing
    return redirect('eCommerce:main_cart_page')


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
        return redirect('vendor_dashboard')

    return render(request, 'eCommerce/vendor/create_store.html')


@vendor_required
def edit_store(request, store_id):
    store = get_object_or_404(Store, id=store_id, vendor=request.user)
    if request.method == 'POST':
        store.name = request.POST.get('name')
        store.description = request.POST.get('description')
        store.save()
        messages.success(request, "Store updated successfully!")
        return redirect('vendor_dashboard')

    return render(request, 'eCommerce/vendor/edit_store.html', {'store': store})


@vendor_required
def delete_store(request, store_id):
    store = get_object_or_404(Store, id=store_id, vendor=request.user)
    store.delete()
    messages.success(request, "Store deleted successfully!")
    return redirect('vendor_dashboard')


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
        return redirect('vendor_store_products', store_id=store.id)

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


@buyer_required
def buyer_home(request):
    """Main buyer homepage - show all active products"""
    products = Product.objects.filter(is_active=True).select_related('store')
    stores = Store.objects.filter(is_active=True)

    return render(request, 'eCommerce/buyer/home.html', {
        'products': products,
        'stores': stores,
    })


@buyer_required
def product_detail(request, product_id):
    """View single product + reviews"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    reviews = product.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        Review.objects.create(
            product=product,
            buyer=request.user,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Review submitted successfully!")
        return redirect('product_detail', product_id=product.id)

    return render(request, 'eCommerce/buyer/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
    })


@buyer_required
def add_to_cart(request, product_id):
    """Add product to buyer's cart (using model, not session)"""
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Get or create cart for this buyer
    cart, created = Cart.objects.get_or_create(buyer=request.user)

    cart_item, created = Cart_Item.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} added to cart!")
    return redirect('main_cart_page')


@buyer_required
def view_cart(request):
    """Show cart with totals"""
    try:
        cart = Cart.objects.get(buyer=request.user)
        items = cart.items.select_related('product')

        total = sum(item.product.price * item.quantity for item in items)
    except Cart.DoesNotExist:
        items = []
        total = 0

    return render(request, 'eCommerce/main_cart_page.html', {
        'cart': items,
        'total_price': total,
    })


@buyer_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    Cart_Item.objects.filter(id=item_id, cart__buyer=request.user).delete()
    messages.success(request, "Item removed from cart.")
    return redirect('main_cart_page')
