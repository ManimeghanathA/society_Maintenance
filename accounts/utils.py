from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Profile


def create_resident_user(name, email, password, phone="", role=Profile.RESIDENT):
    email = email.lower()
    first_name, _, last_name = name.partition(" ")
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_staff=role == Profile.ADMIN,
        is_superuser=role == Profile.ADMIN,
    )
    Profile.objects.update_or_create(user=user, defaults={"role": role, "phone": phone})
    return user


def send_account_created_email(user, password=None):
    body = f"Hello {user.get_full_name() or user.email},\n\nYour Society Maintenance Tracker account has been created.\nLogin ID: {user.email}\n"
    if password:
        body += f"Temporary password: {password}\n"
    body += "\nPlease log in and change your password."
    try:
        send_mail("Society Maintenance account created", body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
    except Exception:
        pass


def send_password_setup_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    path = reverse("password_setup", args=[uid, token])
    setup_url = request.build_absolute_uri(path)
    body = (
        f"Hello {user.get_full_name() or user.email},\n\n"
        "Your Society Maintenance Tracker account has been approved.\n"
        "Set your password privately using this one-time link:\n\n"
        f"{setup_url}\n\n"
        "If you did not request this account, ignore this email."
    )
    try:
        send_mail("Set up your Society Maintenance password", body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
    except Exception:
        pass
