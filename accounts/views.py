from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode

from .decorators import role_required
from .forms import EmailLoginForm, PasswordChangeSimpleForm, PasswordSetupForm, RegistrationRequestForm, ResidentCreateForm
from .models import Profile, RegistrationRequest
from .utils import create_resident_user, send_account_created_email, send_password_setup_email


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = EmailLoginForm(request.POST or None)
    selected_role = request.POST.get("role", Profile.RESIDENT)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].lower()
        password = form.cleaned_data["password"]
        if not User.objects.filter(username=email).exists():
            if selected_role == Profile.ADMIN:
                messages.error(request, "Admin email not found.")
                return render(request, "accounts/login.html", {"form": form, "selected_role": selected_role})
            request.session["attempted_email"] = email
            messages.info(request, "We could not find that email. Send a create request to admin.")
            return redirect("registration_request")
        user = authenticate(request, username=email, password=password)
        if user:
            profile = getattr(user, "profile", None)
            if not profile or profile.role != selected_role:
                messages.error(request, f"Please use the correct {profile.role if profile else 'user'} login section.")
                return render(request, "accounts/login.html", {"form": form, "selected_role": selected_role})
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid password.")
    return render(request, "accounts/login.html", {"form": form, "selected_role": selected_role})


def logout_view(request):
    logout(request)
    return redirect("login")


def registration_request_view(request):
    initial = {
        "email": request.session.get("attempted_email", ""),
    }
    form = RegistrationRequestForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        req = form.save(commit=False)
        req.email = req.email.lower()
        req.save()
        messages.success(request, "Create request sent to admin. You will receive a private password setup link if approved.")
        return redirect("login")
    return render(request, "accounts/registration_request.html", {"form": form})


@login_required
def home(request):
    profile = getattr(request.user, "profile", None)
    if profile and profile.role == Profile.ADMIN:
        return redirect("admin_dashboard")
    return redirect("resident_home")


@login_required
def change_password(request):
    form = PasswordChangeSimpleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not request.user.check_password(form.cleaned_data["current_password"]):
            messages.error(request, "Current password is incorrect.")
        else:
            request.user.set_password(form.cleaned_data["new_password"])
            request.user.save()
            messages.success(request, "Password changed. Please log in again.")
            return redirect("login")
    return render(request, "accounts/change_password.html", {"form": form})


@login_required
def profile_view(request):
    profile = getattr(request.user, "profile", None)
    return render(request, "accounts/profile.html", {"profile": profile})


@role_required(Profile.ADMIN)
def resident_list(request):
    residents_qs = User.objects.filter(profile__role=Profile.RESIDENT).select_related("profile").prefetch_related("complaints")
    residents = Paginator(residents_qs, 10).get_page(request.GET.get("page"))
    return render(request, "accounts/resident_list.html", {"residents": residents})


@role_required(Profile.ADMIN)
def create_resident(request):
    form = ResidentCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        role = form.cleaned_data["role"]
        user = create_resident_user(form.cleaned_data["name"], form.cleaned_data["email"], form.cleaned_data["password"], form.cleaned_data["phone"], role)
        send_account_created_email(user, form.cleaned_data["password"])
        messages.success(request, f"{role.title()} account created and email sent.")
        return redirect("admin_dashboard" if role == Profile.ADMIN else "resident_list")
    return render(request, "accounts/create_resident.html", {"form": form})


@role_required(Profile.ADMIN)
def registration_requests(request):
    requests = Paginator(RegistrationRequest.objects.all(), 10).get_page(request.GET.get("page"))
    return render(request, "accounts/registration_requests.html", {"requests": requests})


@role_required(Profile.ADMIN)
def review_registration_request(request, pk, action):
    req = get_object_or_404(RegistrationRequest, pk=pk, status=RegistrationRequest.PENDING)
    if action == "approve":
        if User.objects.filter(username=req.email.lower()).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect("registration_requests")
        user = create_resident_user(req.name, req.email, None)
        user.set_unusable_password()
        user.save()
        send_password_setup_email(request, user)
        req.status = RegistrationRequest.APPROVED
        messages.success(request, "Request approved. A private password setup link was emailed to the resident.")
    else:
        req.status = RegistrationRequest.REJECTED
        messages.info(request, "Request rejected.")
    req.reviewed_by = request.user
    req.reviewed_at = timezone.now()
    req.save()
    return redirect("registration_requests")


def password_setup(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        user = None
    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "That password setup link is invalid or expired.")
        return redirect("login")

    form = PasswordSetupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user.set_password(form.cleaned_data["new_password"])
        user.save()
        messages.success(request, "Password set. You can now log in.")
        return redirect("login")
    return render(request, "accounts/password_setup.html", {"form": form, "setup_user": user})
