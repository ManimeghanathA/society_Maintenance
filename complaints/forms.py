from django import forms

from .models import Complaint


class ComplaintCreateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["category", "description", "image"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }


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
