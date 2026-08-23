from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

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
