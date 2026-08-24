from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

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

    def test_resident_cannot_view_another_residents_complaint(self):
        complaint = Complaint.objects.create(resident=self.other, category="Security", description="Gate issue")
        self.client.login(username="resident@example.com", password="residentpass")
        response = self.client.get(reverse("complaint_detail", args=[complaint.id]))
        self.assertRedirects(response, reverse("my_complaints"))

    def test_resident_can_create_complaint_without_image(self):
        self.client.login(username="resident@example.com", password="residentpass")
        response = self.client.post(reverse("create_complaint"), {"category": "Plumbing", "description": "Water leak"})
        self.assertRedirects(response, reverse("my_complaints"))
        complaint = Complaint.objects.get(description="Water leak")
        self.assertEqual(complaint.status, Complaint.OPEN)
        self.assertTrue(ComplaintHistory.objects.filter(complaint=complaint, note="Complaint raised").exists())

    def test_overdue_calculation_uses_deadline(self):
        complaint = Complaint.objects.create(
            resident=self.resident,
            category="Cleaning",
            description="Missed cleaning",
            deadline=timezone.localdate() - timezone.timedelta(days=1),
        )
        self.assertTrue(complaint.is_overdue)

    def test_export_filtered_complaints_csv(self):
        Complaint.objects.create(resident=self.resident, category="Lift", description="Lift noise")
        self.client.login(username="admin@example.com", password="adminpass")
        response = self.client.get(reverse("admin_complaints"), {"export": "csv", "category": "Lift"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("Lift", response.content.decode())
