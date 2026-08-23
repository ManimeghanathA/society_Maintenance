from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile
from .models import Notification, Notice


class NoticeFlowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin@example.com", email="admin@example.com", password="adminpass", is_staff=True)
        Profile.objects.update_or_create(user=self.admin, defaults={"role": Profile.ADMIN})
        self.resident = User.objects.create_user(username="resident@example.com", email="resident@example.com", password="residentpass")
        Profile.objects.create(user=self.resident, role=Profile.RESIDENT)

    def test_important_notice_creates_resident_notification(self):
        self.client.login(username="admin@example.com", password="adminpass")
        response = self.client.post(reverse("create_notice"), {"title": "Water shutdown", "body": "Tomorrow morning", "important": "on"})
        self.assertRedirects(response, reverse("notice_board"))
        self.assertTrue(Notice.objects.filter(title="Water shutdown", important=True).exists())
        self.assertTrue(Notification.objects.filter(user=self.resident, message__icontains="Water shutdown").exists())

    def test_admin_can_delete_notice(self):
        notice = Notice.objects.create(title="Old notice", body="Remove this", created_by=self.admin)
        self.client.login(username="admin@example.com", password="adminpass")
        response = self.client.post(reverse("delete_notice", args=[notice.id]))
        self.assertRedirects(response, reverse("notice_board"))
        self.assertFalse(Notice.objects.filter(id=notice.id).exists())

    def test_resident_cannot_delete_notice(self):
        notice = Notice.objects.create(title="Keep notice", body="Resident cannot remove", created_by=self.admin)
        self.client.login(username="resident@example.com", password="residentpass")
        response = self.client.post(reverse("delete_notice", args=[notice.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("home"))
        self.assertTrue(Notice.objects.filter(id=notice.id).exists())
