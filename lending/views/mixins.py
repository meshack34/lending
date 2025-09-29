# lending/views/mixins.py
from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator

# Shortcuts
admin_required   = role_required("ADMIN")
manager_required = role_required("MANAGER")
officer_required = role_required("OFFICER")
member_required  = role_required("MEMBER")
