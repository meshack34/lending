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

# lending/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def role_required(role):
    """
    Generic decorator to ensure the logged in user has the given role.
    Usage: @role_required("MANAGER")
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            # ensure user has `role` attribute
            if not hasattr(request.user, "role") or request.user.role != role:
                messages.error(request, "You are not authorized to access this page.")
                # redirect to a safe page — adjust 'dashboard' if you use different names
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# specific role decorators
def admin_required(view_func):
    return role_required("ADMIN")(view_func)

def manager_required(view_func):
    return role_required("MANAGER")(view_func)

def officer_required(view_func):
    return role_required("OFFICER")(view_func)

def member_required(view_func):
    return role_required("MEMBER")(view_func)
