""""
Tests for models
"""
from decimal import Decimal

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from unittest.mock import patch

from core import models


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            username = "usernameexample"
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"]
        ]
        for i, (email, expected) in enumerate(sample_emails):
            user = get_user_model().objects.create_user(
                email = email, password = "sample123", userPhoneNumber=f"1234567890{i}", username=f"exampleuser{i}")
            self.assertEqual(user.email, expected)

    def test_create_user_with_unique_phone_number(self):
        """Test creating a user with a unique phone nubmer"""
        user1 = get_user_model().objects.create_user(
            email="test1@example.com",
            password="testpass123",
            userPhoneNumber="+16502530000",
            username = "username1",
        )

        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(
                email="test2@example.com",
                password="testpass123",
                userPhoneNumber=user1.userPhoneNumber,
                username = "username2"
            )

    def test_create_user_with_unique_username(self):
        """Test creating a user with a unique username """
        username = "testuser"
        email1 = "test1@example.com"
        email2 = "test2@example.com"
        password = "testpass123"

        user1 = get_user_model().objects.create_user(
            email=email1,
            password = password,
            userPhoneNumber = "+16502530000",
            username=username
        )

        with self.assertRaises(IntegrityError):
            user2 = get_user_model().objects.create_user(
                email = email2,
                password = password,
                userPhoneNumber = "+16502530001",
                username=username
            )


    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")


    def test_new_user_without_username_raises_error(self):
        """Test that creating a user without an username raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email = "test1@example.com",
                password = "testpass123",
                username =""
            )


    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "test123",
        )

    def test_create_post(self):
        """Test creating a post is successful"""
        user = get_user_model().objects.create_user(
            email = "test@example.com",
            password = "testpass123",
            username = "username1123"
        )
        post = models.Post.objects.create(
            user = user,
            postReview = "Sample post review",
            postRatingDelicious = 5,
            postRatingEatAgain = 5,
            postRatingWorthIt =5
        )

        self.assertEqual(str(post), post.postReview)

    @patch("core.models.uuid.uuid4")
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path"""
        uuid = "test-uuid",
        mock_uuid.return_value = uuid
        user = get_user_model().objects.create(
            email = "test@example.com",
            password = "testpass123",
            username = "username1123"
        )
        post = models.Post.objects.create(
            user=user,
            postReview = 5,
            postRatingDelicious = 5,
            postRatingEatAgain = 5,
            postRatingWorthIt = 5
        )
        file_path = models.post_image_file_path(post, "example.jpg")

        self.assertEqual(file_path, f"uploads/posts/user{user.id}/images/{uuid}.jpg")