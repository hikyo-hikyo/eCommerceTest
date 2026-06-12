
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def vendor_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_vendor:
            messages.error(
                request, "You must be a vendor to access this page.")
            return redirect('eCommerce:buyer_home') if request.user.is_buyer else redirect('grabsomore:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def buyer_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_buyer:
            messages.error(request, "You must be a buyer to access this page.")
            return redirect('eCommerce:vendor_dashboard') if request.user.is_vendor else redirect('grabsomore:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
