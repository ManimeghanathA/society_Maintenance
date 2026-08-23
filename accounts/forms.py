from django import forms
from django.contrib.auth.models import User

from .models import Profile, RegistrationRequest


class EmailLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email ID"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))


class RegistrationRequestForm(forms.ModelForm):
    class Meta:
        model = RegistrationRequest
        fields = ["name", "email", "requested_password"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "requested_password": forms.TextInput(attrs={"class": "form-control"}),
        }


class ResidentCreateForm(forms.Form):
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))
    name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class PasswordChangeSimpleForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    new_password = forms.CharField(min_length=6, widget=forms.PasswordInput(attrs={"class": "form-control"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("new_password") != cleaned.get("confirm_password"):
            raise forms.ValidationError("New passwords do not match.")
        return cleaned
