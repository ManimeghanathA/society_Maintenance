from django import forms

from .models import Notice


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ["title", "body", "important"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "important": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
