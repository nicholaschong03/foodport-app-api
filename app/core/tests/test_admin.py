"""
Tests for the Django admin modifications
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminSiteTest(TestCase):
    """Tests for Django admin"""

    def setUp(self):
        """Create user and clients"""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            userEmailAddress = "chong@example.com",
            password = "12345"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            userEmailAddress="user@example.com",
            password = "testpass123",
            userPhoneNumber = "0123456788",
            userName = "Test User ",
            userUsername = "sample username"
        )

    def test_users_list(self):
        """Test that users are listed on page."""
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.userName)
        self.assertContains(res, self.user.userEmailAddress)

    def test_edit_user_page(self):
        """Test the edit user page works"""
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works. """
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)