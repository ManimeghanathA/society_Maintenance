from django.contrib.auth.models import User
from django.db import models


class Notice(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    important = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="notices")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-important", "-created_at"]

    def __str__(self):
        return self.title


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.message
