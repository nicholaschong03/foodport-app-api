from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status

import tempfile
import os

from PIL import Image

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")
LOGOUT_URL = reverse("user:logout")
IMAGE_URL = reverse("user:upload_profile_image")


def detail_url(user_id):
    """Create and return the URL for retrieving a user's profile"""
    return reverse("user:other_user", args=[user_id])


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public fatures of the user API"""
    
    def setUP(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creaing user is successful"""
        payload = {
            "userEmailAddress": "test@example.com",
            "password": "testpass123",
            "userName": "Test Name",
            "userPhoneNumber": "+60123456789",
            "userUsername": "Test username",
                }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(userEmailAddress=payload['userEmailAddress'])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_with_email_exist_error(self):
        """Test error returned if user with email exists"""
        payload = {
            "userEmailAddress": "test@example.com",
            "password": "testpass123",
            "userUsername": "Test username",
            "userName": "Test Name",
            "userPhoneNumber": "+60123456789",

        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            "userEmailAddress": "test@example.com",
            "password": "pw",
            "userName": "Test name",
            "userPhoneNumber": "+60123456789",
            "userUsername": "Test username"
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            userEmailAddress=payload["userEmailAddress"]
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials"""
        user_details = {
            "userName": "Test Name",
            "userEmailAddress": "test@example.com",
            "password": "test-user-password123",
            "userPhoneNumber": "+60123456789",
            "userUsername": "Test username"
        }
        create_user(**user_details)

        payload = {
            "userEmailAddress": user_details["userEmailAddress"],
            "password": user_details["password"],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("idToken", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid"""
        create_user(userEmailAddress="test@example.com",
                    password="goodpass",
                    userPhoneNumber="+60123456789",
                    userUsername="test username"
                    )

        payload = {
            "userEmailAddress": "test@example.com",
            "password": "badpass",
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error"""
        payload = {
            "userEmailAddress": "test@example.com",
            "password": "",

        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)



class PrivateUserApiTest(TestCase):
    """Test API requests that require authentication."""

    def setUp(self):
        self.user = create_user(
            userEmailAddress="test@example.com",
            password="testpass123",
            userName="Test Name",
            userPhoneNumber="+60123456789",
            userUsername = "test username"
        )
        self.client = APIClient()
        self.token = Token.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user, token=self.token)

    def test_retrieve_profile_success(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictContainsSubset({
            "userName": self.user.userName,
            "userEmailAddress": self.user.userEmailAddress,
            "userPhoneNumber": self.user.userPhoneNumber,
            "userUsername": self.user.userUsername
        }, res.data)

    def test_retrieve_other_profile_success(self):
        """Test retrieving other users' profile"""
        other_user = create_user(
            userEmailAddress="user0@example.com",
            password = "user0password",
            userName = "user0name",
            userPhoneNumber = "+601234567890",
            userUsername = "user0username"
        )
        url = detail_url(other_user.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertDictContainsSubset({
            "userName": other_user.userName,
            "userEmailAddress": other_user.userEmailAddress,
            "userPhoneNumber": other_user.userPhoneNumber,
            "userUsername": other_user.userUsername
        }, res.data)

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the ME endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profiles(self):
        """Test updating the user profile for the authenticated user"""
        payload = {"userName": "Updated name", "password": "newpassword123"}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.userName, payload["userName"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_log_out_user(self):
        """Test logging out for authenticated users"""
        res = self.client.post(LOGOUT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {"message": "Successfully logged out"})
        self.assertFalse(Token.objects.filter(user=self.user).exists())


class ImageUploadTests(TestCase):
    """Test for the profile picture upload API"""

    def setUp(self):
        self.user = create_user(
            userEmailAddress="test@example.com",
            password="testpass123",
            userName="Test Name",
            userPhoneNumber="+60123456789",
            userUsername = "test username"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def tearDown(self):
        self.user.userProfilePictureUrl.delete()

    def test_upload_image(self):
        """Test uploading an image to a post"""
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10,10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {"userProfilePictureUrl": image_file}
            res = self.client.post(IMAGE_URL, payload, format="multipart")

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("userProfilePictureUrl", res.data)
        self.assertTrue(os.path.exists(self.user.userProfilePictureUrl.path))



