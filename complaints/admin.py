from django.contrib import admin

from .models import Complaint, ComplaintHistory


admin.site.register(Complaint)
admin.site.register(ComplaintHistory)
