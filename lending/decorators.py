# lending/decorators.py
from django.shortcuts import redirect
from django.contrib import messages

def member_required(view_func):
    """Ensure only members can access this view."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not hasattr(request.user, "role") or request.user.role != "MEMBER":
            messages.error(request, "You are not authorized to access this page.")
            return redirect("dashboard")  # or another safe page
        return view_func(request, *args, **kwargs)
    return wrapper

# lending/decorators.py
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """Ensure only admins can access this view."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not hasattr(request.user, "role") or request.user.role != "ADMIN":
            messages.error(request, "You are not authorized to access this page.")
            return redirect("dashboard")  # or another safe page
        return view_func(request, *args, **kwargs)
    return wrapper
