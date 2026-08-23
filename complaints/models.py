from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Complaint(models.Model):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    STATUS_CHOICES = (
        (OPEN, "Open"),
        (IN_PROGRESS, "In Progress"),
        (RESOLVED, "Resolved"),
    )

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PRIORITY_CHOICES = (
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
    )

    CATEGORY_CHOICES = (
        ("Plumbing", "Plumbing"),
        ("Electrical", "Electrical"),
        ("Lift", "Lift"),
        ("Security", "Security"),
        ("Cleaning", "Cleaning"),
        ("Parking", "Parking"),
        ("Other", "Other"),
    )

    resident = models.ForeignKey(User, on_delete=models.CASCADE, related_name="complaints")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    image = models.ImageField(upload_to="complaints/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=MEDIUM)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "deadline", "-created_at"]

    @property
    def is_overdue(self):
        if self.status == self.RESOLVED:
            return False
        if self.deadline:
            return self.deadline < timezone.localdate()
        return (timezone.now() - self.created_at).days > settings.OVERDUE_DAYS

    @property
    def code(self):
        return f"CMP-{self.id:04d}"

    def __str__(self):
        return f"{self.code} - {self.category}"


class ComplaintHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="history")
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="complaint_updates")
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.complaint.code}: {self.old_status} -> {self.new_status}"
