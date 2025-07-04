# recommendations/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def admin_required(view_func):
    """
    Allow access only if the visitor:
    • is authenticated, and
    • has an active Admin profile row.
    Otherwise redirect to the admin login page.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        ok = (
            request.user.is_authenticated
            and hasattr(request.user, "admin_profile")
            and request.user.admin_profile.is_active
        )
        if ok:
            return view_func(request, *args, **kwargs)

        # bounce them to login, preserving ?next=…
        login_url = reverse("admin_login")
        return redirect(f"{login_url}?next={request.path}")
    return _wrapped
