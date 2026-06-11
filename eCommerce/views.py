from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import Product

def view_product_page(request):
    user = request.user  # Get the current logged-in user

    # Check if user has permission to view products
    if user.has_perm('eCommerce.view_product') or user.has_perm('eCommerce.view_products'):
        if request.method == 'POST':
            product_name = request.POST.get('product')  # Get product name from form submission

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
            product_name = request.POST.get('product')  # Get product name from form
            new_price = request.POST.get('new_price')  # Get new price from form

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
