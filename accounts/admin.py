from django.contrib import admin

from .models import Profile, RegistrationRequest


admin.site.register(Profile)
admin.site.register(RegistrationRequest)
