# grabsomore/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import secrets
from hashlib import sha1
from django.utils import timezone
from datetime import timedelta

# Email
from django.core.mail import EmailMessage

# Your custom models and forms
from accounts.models import User
from accounts.forms import UserRegistrationForm
from .models import ResetToken
from .utils import build_email


# ===================== LOGIN =====================
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully!")

            if user.is_vendor:
                return redirect('eCommerce:vendor_dashboard')
            else:
                return redirect('grabsomore:welcome')
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'grabsomore/login.html')

    return render(request, 'grabsomore/login.html')


# ===================== REGISTER =====================
# grabsomore/views.py
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, f"✅ Account created successfully! Welcome {user.username}")
            return redirect('eCommerce:buyer_home')
        else:
            # Force show errors
            messages.error(request, "Please correct the errors below.")
            print("=== FORM ERRORS ===")
            print(form.errors)          # ← Check your terminal!
    else:
        form = UserRegistrationForm()

    return render(request, 'grabsomore/register.html', {'form': form})


# ===================== LOGOUT =====================
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('grabsomore:login')


# ===================== WELCOME =====================
@login_required(login_url=reverse_lazy('grabsomore:login'))
def welcome(request):
    return render(request, 'grabsomore/welcome.html')


# ===================== PASSWORD RESET =====================
def change_user_password(username, new_password):
    user = User.objects.get(username=username)
    user.set_password(new_password)
    user.save()


def generate_reset_url(user):
    domain = "http://127.0.0.1:8000/"
    token = secrets.token_urlsafe(16)
    expiry_date = timezone.now() + timedelta(minutes=5)
    hashed_token = sha1(token.encode()).hexdigest()

    ResetToken.objects.create(
        user=user,
        token=hashed_token,
        expiry_date=expiry_date
    )

    return f"{domain}grabsomore/reset_password/{token}/"


def send_password_reset(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        try:
            user = User.objects.get(email=user_email)
            reset_url = generate_reset_url(user)
            email = build_email(user, reset_url)
            email.send()
        except ObjectDoesNotExist:
            pass  # Still show success to prevent email enumeration

        return render(request, 'grabsomore/reset_email_sent.html', {'email': user_email})

    return render(request, 'grabsomore/request_password_reset.html')


def reset_user_password(request, token):
    hashed_token = sha1(token.encode()).hexdigest()

    try:
        user_token = ResetToken.objects.get(token=hashed_token)

        if user_token.expiry_date.replace(tzinfo=None) < datetime.now():
            user_token.delete()
            return render(request, 'grabsomore/password_reset_expired.html')

        request.session['user_id'] = user_token.user.id
        request.session['reset_token'] = token

        return render(request, 'grabsomore/password_reset.html', {'token': token})

    except ResetToken.DoesNotExist:
        return render(request, 'grabsomore/password_reset_invalid.html')


def reset_password(request):
    if request.method == 'POST':
        token = request.session.get('reset_token')
        password = request.POST.get('password')
        password_conf = request.POST.get('password_conf')

        if password != password_conf:
            return render(request, 'grabsomore/password_reset.html', {
                'error': 'Passwords do not match.',
                'token': token
            })

        try:
            user_id = request.session.get('user_id')
            user = User.objects.get(id=user_id)
            hashed_token = sha1(token.encode()).hexdigest()
            reset_token = ResetToken.objects.get(token=hashed_token)

            if reset_token.expiry_date.replace(tzinfo=None) < datetime.now():
                reset_token.delete()
                return render(request, 'grabsomore/password_reset_expired.html')

            user.set_password(password)
            user.save()
            reset_token.delete()
            request.session.flush()

            messages.success(
                request, "Password reset successfully! Please log in.")
            return redirect('grabsomore:login')

        except (User.DoesNotExist, ResetToken.DoesNotExist):
            return render(request, 'grabsomore/password_reset_invalid.html')

    return redirect('grabsomore:login')
