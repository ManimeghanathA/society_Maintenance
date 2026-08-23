from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from notices.models import Notification
from .models import Complaint, ComplaintHistory


class ComplaintFlowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin@example.com", email="admin@example.com", password="adminpass", is_staff=True)
        Profile.objects.update_or_create(user=self.admin, defaults={"role": Profile.ADMIN})
        self.resident = User.objects.create_user(username="resident@example.com", email="resident@example.com", password="residentpass")
        Profile.objects.create(user=self.resident, role=Profile.RESIDENT)
        self.other = User.objects.create_user(username="other@example.com", email="other@example.com", password="otherpass")
        Profile.objects.create(user=self.other, role=Profile.RESIDENT)

    def test_resident_sees_only_my_complaints(self):
        mine = Complaint.objects.create(resident=self.resident, category="Plumbing", description="Leak")
        Complaint.objects.create(resident=self.other, category="Lift", description="Stuck")
        self.client.login(username="resident@example.com", password="residentpass")
        response = self.client.get(reverse("my_complaints"))
        self.assertContains(response, mine.code)
        self.assertNotContains(response, "Lift")

    def test_admin_status_update_creates_history_and_notification(self):
        complaint = Complaint.objects.create(resident=self.resident, category="Electrical", description="Spark")
        self.client.login(username="admin@example.com", password="adminpass")
        response = self.client.post(
            reverse("update_complaint", args=[complaint.id]),
            {"priority": "high", "status": "in_progress", "deadline": "", "note": "Assigned to electrician"},
        )
        self.assertRedirects(response, reverse("complaint_detail", args=[complaint.id]))
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, Complaint.IN_PROGRESS)
        self.assertTrue(ComplaintHistory.objects.filter(complaint=complaint, note="Assigned to electrician").exists())
        self.assertTrue(Notification.objects.filter(user=self.resident, message__icontains=complaint.code).exists())
