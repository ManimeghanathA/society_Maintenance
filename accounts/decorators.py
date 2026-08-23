from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            if getattr(request.user, "profile", None) and request.user.profile.role == role:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission to access that page.")
            return redirect("home")

        return wrapper

    return decorator
