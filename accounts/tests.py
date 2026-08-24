from django.contrib.auth.models import User
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Profile, RegistrationRequest


class AccountFlowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin@example.com", email="admin@example.com", password="adminpass", is_staff=True)
        Profile.objects.update_or_create(user=self.admin, defaults={"role": Profile.ADMIN})

    def test_unknown_email_can_submit_editable_registration_request(self):
        response = self.client.post(reverse("login"), {"email": "new@example.com", "password": "wantedpass", "role": "resident"})
        self.assertRedirects(response, reverse("registration_request"))
        response = self.client.post(reverse("registration_request"), {"name": "New Resident", "email": "edited@example.com"})
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(RegistrationRequest.objects.filter(email="edited@example.com").exists())

    def test_user_must_login_from_matching_role_section(self):
        User.objects.create_user(username="resident@example.com", email="resident@example.com", password="residentpass")
        user = User.objects.get(username="resident@example.com")
        Profile.objects.create(user=user, role=Profile.RESIDENT)
        response = self.client.post(reverse("login"), {"email": "resident@example.com", "password": "residentpass", "role": "admin"})
        self.assertContains(response, "Please use the correct resident login section.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_approval_creates_resident_and_sends_password_setup(self):
        req = RegistrationRequest.objects.create(name="Resident One", email="resident@example.com")
        self.client.login(username="admin@example.com", password="adminpass")
        response = self.client.get(reverse("review_registration_request", args=[req.id, "approve"]))
        self.assertRedirects(response, reverse("registration_requests"))
        user = User.objects.get(username="resident@example.com")
        self.assertEqual(user.profile.role, Profile.RESIDENT)
        self.assertFalse(user.has_usable_password())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("password-setup", mail.outbox[0].body)

    def test_password_setup_link_sets_private_password(self):
        user = User.objects.create_user(username="setup@example.com", email="setup@example.com")
        user.set_unusable_password()
        user.save()
        Profile.objects.create(user=user, role=Profile.RESIDENT)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        response = self.client.post(reverse("password_setup", args=[uid, token]), {"new_password": "privatepass", "confirm_password": "privatepass"})
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(self.client.login(username="setup@example.com", password="privatepass"))

    def test_resident_cannot_access_admin_dashboard(self):
        resident = User.objects.create_user(username="resident2@example.com", email="resident2@example.com", password="residentpass")
        Profile.objects.create(user=resident, role=Profile.RESIDENT)
        self.client.login(username="resident2@example.com", password="residentpass")
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("home"))
