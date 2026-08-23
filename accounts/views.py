from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .decorators import role_required
from .forms import EmailLoginForm, PasswordChangeSimpleForm, RegistrationRequestForm, ResidentCreateForm
from .models import Profile, RegistrationRequest
from .utils import create_resident_user, send_account_created_email


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
            request.session["attempted_password"] = password
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
        "requested_password": request.session.get("attempted_password", ""),
    }
    form = RegistrationRequestForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        req = form.save(commit=False)
        req.email = req.email.lower()
        req.save()
        messages.success(request, "Create request sent to admin.")
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
    residents = User.objects.filter(profile__role=Profile.RESIDENT).select_related("profile").prefetch_related("complaints")
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
    requests = RegistrationRequest.objects.all()
    return render(request, "accounts/registration_requests.html", {"requests": requests})


@role_required(Profile.ADMIN)
def review_registration_request(request, pk, action):
    req = get_object_or_404(RegistrationRequest, pk=pk, status=RegistrationRequest.PENDING)
    if action == "approve":
        if User.objects.filter(username=req.email.lower()).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect("registration_requests")
        user = create_resident_user(req.name, req.email, req.requested_password)
        send_account_created_email(user, req.requested_password)
        req.status = RegistrationRequest.APPROVED
        messages.success(request, "Request approved and resident account created.")
    else:
        req.status = RegistrationRequest.REJECTED
        messages.info(request, "Request rejected.")
    req.reviewed_by = request.user
    req.reviewed_at = timezone.now()
    req.save()
    return redirect("registration_requests")
