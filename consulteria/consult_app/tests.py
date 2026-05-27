from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardAndProfileTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="testpass123",
        )

    def test_anonymous_dashboard_redirects_to_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_authenticated_dashboard_renders(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, tester")

    def test_authenticated_profile_edit_renders_without_existing_profile(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("edit_profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Profile")

    def test_signup_with_template_field_names_creates_usable_password(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "StrongPass123",
                "password2": "StrongPass123",
            },
        )

        user = self.User.objects.get(username="newuser")

        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.check_password("StrongPass123"))

    def test_login_with_created_user_redirects_to_dashboard(self):
        self.User.objects.create_user(
            username="loginuser",
            email="loginuser@example.com",
            password="LoginPass123",
        )

        response = self.client.post(
            reverse("login"),
            {"username": "loginuser", "password": "LoginPass123"},
        )

        self.assertRedirects(response, reverse("dashboard"))
