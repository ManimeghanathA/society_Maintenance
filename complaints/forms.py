from django import forms
from django.conf import settings

from .models import Complaint


class ComplaintCreateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["category", "description", "image"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "image": forms.FileInput(attrs={"class": "form-control", "accept": "image/jpeg,image/png,image/webp"}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            return image
        if image.size > settings.MAX_UPLOAD_SIZE:
            max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            raise forms.ValidationError(f"Image must be {max_mb:.0f} MB or smaller.")
        content_type = getattr(image, "content_type", "")
        if content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise forms.ValidationError("Only JPEG, PNG, or WebP images are allowed.")
        return image


class ComplaintAdminUpdateForm(forms.ModelForm):
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))

    class Meta:
        model = Complaint
        fields = ["priority", "status", "deadline", "note"]
        widgets = {
            "priority": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "deadline": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }
