from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile, RegistrationRequest


class AccountFlowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin@example.com", email="admin@example.com", password="adminpass", is_staff=True)
        Profile.objects.update_or_create(user=self.admin, defaults={"role": Profile.ADMIN})

    def test_unknown_email_can_submit_editable_registration_request(self):
        response = self.client.post(reverse("login"), {"email": "new@example.com", "password": "wantedpass", "role": "resident"})
        self.assertRedirects(response, reverse("registration_request"))
        response = self.client.post(reverse("registration_request"), {"name": "New Resident", "email": "edited@example.com", "requested_password": "editedpass"})
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(RegistrationRequest.objects.filter(email="edited@example.com", requested_password="editedpass").exists())

    def test_user_must_login_from_matching_role_section(self):
        User.objects.create_user(username="resident@example.com", email="resident@example.com", password="residentpass")
        user = User.objects.get(username="resident@example.com")
        Profile.objects.create(user=user, role=Profile.RESIDENT)
        response = self.client.post(reverse("login"), {"email": "resident@example.com", "password": "residentpass", "role": "admin"})
        self.assertContains(response, "Please use the correct resident login section.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_approval_creates_resident_with_email_login(self):
        req = RegistrationRequest.objects.create(name="Resident One", email="resident@example.com", requested_password="residentpass")
        self.client.login(username="admin@example.com", password="adminpass")
        response = self.client.get(reverse("review_registration_request", args=[req.id, "approve"]))
        self.assertRedirects(response, reverse("registration_requests"))
        user = User.objects.get(username="resident@example.com")
        self.assertEqual(user.profile.role, Profile.RESIDENT)
        self.assertTrue(self.client.login(username="resident@example.com", password="residentpass"))
