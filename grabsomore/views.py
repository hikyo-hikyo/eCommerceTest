# To show HTML pages and redirect users
from django.shortcuts import render, redirect

# Functions to handle login and logout
from django.contrib.auth import authenticate, login, logout
# For redirecting users or sending responses
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy  # Helps get URLs by their names
# Makes sure only logged-in users can access pages
from django.contrib.auth.decorators import login_required
from datetime import datetime
import secrets  # For generating secure random tokens
from datetime import timedelta
from hashlib import sha1  # To hash tokens securely
# Better way to handle dates and times in Django
from django.utils import timezone
# For handling cases when an object is not found
from django.core.exceptions import ObjectDoesNotExist
# Helper functions for email and token generation
from .utils import generate_reset_url, build_email
from .models import ResetToken  # Our custom model to store reset tokens

from django.core.mail import EmailMessage  # To send emails
# To hash passwords before saving
from django.contrib.auth.hashers import make_password
from accounts.forms import UserRegistrationForm
from django.contrib import messages

from accounts.models import User


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required

# IMPORTANT: Use your custom User model

# This function handles user login


def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")

            # Redirect based on role
            if user.is_vendor:
                return redirect('vendor_dashboard')
            else:
                return redirect('grabsomore:welcome')   # or your buyer home
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'grabsomore/login.html', {'error': 'Invalid credentials'})

    return render(request, 'grabsomore/login.html')


# This function handles user registration (signing up)
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)                    # Auto-login after register
            messages.success(
                request, f"Account created successfully as {user.get_role_display()}!")

            if user.is_vendor:
                return redirect('vendor_dashboard')
            else:
                return redirect('grabsomore:welcome')
    else:
        form = UserRegistrationForm()

    return render(request, 'grabsomore/register.html', {'form': form})


# Helper function to change a user's password securely
def change_user_password(username, new_password):
    user = User.objects.get(username=username)  # Find user by username

    # Set the new password (hashed automatically)
    user.set_password(new_password)

    user.save()  # Save changes to the database


# Logs the user out and redirects to login page
def logout_user(request):
    if request.user is not None:
        logout(request)  # Log out the current user
        return HttpResponseRedirect(reverse('grabsomore:login'))


# Only logged-in users can see the welcome page
@login_required(login_url=reverse_lazy('grabsomore:login'))
def welcome(request):
    return render(request, 'grabsomore/welcome.html')  # Show the welcome page


# Creates the email object to send for password reset
def build_email(user, reset_url):
    subject = "Password Reset"
    user_email = user.email
    domain_email = "example@domain.com"  # The "from" email address for the email
    body = f"Hi {user.username},\nHere is your link to reset your password: {reset_url}"

    email = EmailMessage(subject, body, domain_email, [user_email])
    return email


# Creates a secure reset URL with a token that expires in 5 minutes
def generate_reset_url(user):
    domain = "http://127.0.0.1:8000/"
    app_name = "grabsomore"  # Make sure this matches your app name in urls.py
    url = f"{domain}{app_name}/reset_password/"

    token = secrets.token_urlsafe(16)  # Generate a random secure token

    expiry_date = timezone.now() + timedelta(minutes=5)  # Token expires in 5 minutes

    # Hash the token to store securely
    hashed_token = sha1(token.encode()).hexdigest()

    # Save the hashed token and expiry date to the database
    reset_token = ResetToken.objects.create(
        user=user,
        token=hashed_token,
        expiry_date=expiry_date
    )

    # Add the raw token (not hashed) to the URL for verification later
    url += f"{token}/"
    return url


# Handles sending the password reset email after user submits their email
def send_password_reset(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        try:
            user = User.objects.get(email=user_email)  # Find user by email
            # Generate reset link with token
            reset_url = generate_reset_url(user)
            email = build_email(user, reset_url)  # Create the email message
            email.send()  # Send the email

            # Show a confirmation page that email was sent
            return render(request, 'grabsomore/reset_email_sent.html', {
                'email': user_email
            })

        except ObjectDoesNotExist:
            # Even if no user found, still show confirmation (to avoid info leaks)
            return render(request, 'grabsomore/reset_email_sent.html', {
                'email': user_email
            })

    # Show the form where user can enter their email
    return render(request, 'grabsomore/request_password_reset.html')


# This view is called when user clicks the reset link in their email
def reset_user_password(request, token):
    hashed_token = sha1(token.encode()).hexdigest()  # Hash the token from URL

    try:
        user_token = ResetToken.objects.get(
            token=hashed_token)  # Look for token in DB

        # Check if the token expired
        if user_token.expiry_date.replace(tzinfo=None) < datetime.now():
            user_token.delete()  # Delete expired token
            # Show expired token message
            return render(request, 'grabsomore/password_reset_expired.html')

        # Save user ID and token in session to verify next step
        request.session['user_id'] = user_token.user.id
        request.session['reset_token'] = token

        # Show the password reset form
        return render(request, 'grabsomore/password_reset.html', {'token': token})

    except ResetToken.DoesNotExist:
        # Token not found or already used
        return render(request, 'grabsomore/password_reset_invalid.html')


# Handles the password reset form submission (when user enters new password)
def reset_password(request):
    if request.method == 'POST':
        username = request.session.get('user')
        token = request.session.get('token')
        password = request.POST.get('password')
        password_conf = request.POST.get('password_conf')

        # Check if all required data is present
        if not all([username, token, password, password_conf]):
            return render(request, 'password_reset.html', {
                'error': 'Missing fields or session expired.',
                'token': token
            })

        # Check if passwords match
        if password != password_conf:
            return render(request, 'password_reset.html', {
                'error': 'Passwords do not match.',
                'token': token
            })

        try:
            user = User.objects.get(username=username)  # Find user by username
            hashed_token = sha1(token.encode()).hexdigest()
            reset_token = ResetToken.objects.get(token=hashed_token)

            # Check token expiry again (just to be sure)
            if reset_token.expiry_date.replace(tzinfo=None) < datetime.now():
                reset_token.delete()
                return render(request, 'password_reset_expired.html')

            # Update the user's password (hashed securely)
            user.password = make_password(password)
            user.save()

            # Delete the token and clear session info
            reset_token.delete()
            request.session.flush()

            # Redirect user to login page after successful password reset
            return HttpResponseRedirect(reverse('grabsomore:login'))

        except (User.DoesNotExist, ResetToken.DoesNotExist):
            return render(request, 'password_reset_invalid.html')

    # If the page was accessed with GET or any other method, redirect to login page
    return HttpResponseRedirect(reverse('grabsomore:login'))
