from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class AccountsAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.email = "testuser@example.com"
        self.password = "securepassword123"

    def test_register_user(self):
        response = self.client.post(reverse("register"), {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "password_confirm": self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username=self.username).exists())

    def test_login_user(self):
        User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        response = self.client.post(reverse("login"), {
            "username": self.username,
            "password": self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_dashboard_access_control_unauthenticated(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_dashboard_access_authenticated(self):
        user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        self.client.force_login(user)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.username)

    def test_logout_user(self):
        user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        self.client.force_login(user)
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)
