from django.http import HttpResponseForbidden
from functools import wraps

def admin_required(view_func):
    """Restrict page access to admin users only."""
    def wrapper(request, *args, **kwargs):
        print(f"🛑 Access Check - Required: Admin, Found: {request.session.get('role')}")
        if request.session.get("role") != "admin":
            return HttpResponseForbidden("Access Denied: Admins only.")
        return view_func(request, *args, **kwargs)
    return wrapper

def user_required(view_func):
    """Restrict page access to normal users and admins only."""
    @wraps(view_func)  # Apply wraps here
    def wrapper(request, *args, **kwargs):
        user_role = request.session.get("role")
        print(f"🛑 Access Check - Required: User/Admin, Found: {user_role}")

        if user_role not in ["user", "admin"]:  # Allow both user and admin
            return HttpResponseForbidden("Access Denied: Users and Admins only.")
        
        return view_func(request, *args, **kwargs)

    return wrapper
