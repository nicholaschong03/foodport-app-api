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
COVER_PICTURE_URL = reverse("user:upload_cover_picture")
USER_LIST_URL = reverse("user:user_list")


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

    def test_user_list_view(self):
        """Test retrieving a list of users"""
        create_user(
            userEmailAddress = "user1@example.com",
            password = "testpass112233",
            userName = "Test Name",
            userPhoneNumber = "+60123456766",
            userUsername = "user1username"
        )
        res = self.client.get(USER_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)

    def test_user_list_search(self):
        """Test searching for a user"""
        other_user = create_user(
            userEmailAddress = "user1@example.com",
            password = "testpass112233",
            userName = "Test Name",
            userPhoneNumber = "+60123456766",
            userUsername = "user1username"
        )

        res = self.client.get(USER_LIST_URL, {"search": "user1username"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]),1)
        self.assertEqual(res.data["results"][0]["userUsername"], other_user.userUsername)

        res = self.client.get(USER_LIST_URL, {"search": "Test Name"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)

    def test_follow_user(self):
        """Test following a user"""
        other_user = create_user(
            userEmailAddress = "user1@example.com",
            password = "testpass112233",
            userName = "Test Name",
            userPhoneNumber = "+60123456543",
            userUsername = "user1username"
        )

        # other_user2 = create_user(
        #     userEmailAddress = "user2@example.com",
        #     password = "testpass112233",
        #     userName = "Test Name2",
        #     userPhoneNumber = "+60123456763",
        #     userUsername = "user2username"
        # )
        #other_user2.following.add(other_user)
        url = reverse("user:follow_user", args=[other_user.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "followed")
        self.assertTrue(other_user in self.user.following.all())

    def test_unfollow_user(self):
        """Test unfollowing user"""
        other_user = create_user(
            userEmailAddress = "user1@example.com",
            password = "testpass112233",
            userName = "Test Name",
            userPhoneNumber = "+60123456543",
            userUsername = "user1username"
        )
        self.user.following.add(other_user)
        url = reverse("user:follow_user", args=[other_user.id])
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "unfollowed")
        self.assertFalse(other_user in self.user.following.all())

    def test_follow_self(self):
        """test folling user ownself"""
        other_user = create_user(
            userEmailAddress = "user1@example.com",
            password = "testpass112233",
            userName = "Test Name",
            userPhoneNumber = "+60123456543",
            userUsername = "user1username"
        )
        url = reverse("user:follow_user", args=[self.user.id])
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["error"], "User cannot follow themselves")

    def test_retrieve_followers(self):
        """Test retrieving a list of followers"""
        other_user = create_user(
            userEmailAddress = "user1@example.com",
            password = "testpass112233",
            userName = "Test Name",
            userPhoneNumber = "+60123456543",
            userUsername = "user1username"
        )

        other_user1 = create_user(
            userEmailAddress = "user2@example.com",
            password = "testpass112233",
            userName = "Test Name 1",
            userPhoneNumber = "+60123456634",
            userUsername = "user2username"
        )

        other_user.following.add(self.user)
        other_user1.following.add(self.user)
        url = reverse("user:followers_list", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),2)
        self.assertEqual(res.data[0]["userUsername"], other_user.userUsername)
        self.assertEqual(res.data[1]["userUsername"], other_user1.userUsername)

    def test_retrieve_followings(self):
        """Test retrieving a following list"""
        other_user = create_user(
            userEmailAddress = "user1@example.com",
            password = "testpass112233",
            userName = "Test Name",
            userPhoneNumber = "+60123456543",
            userUsername = "user1username"
        )

        other_user1 = create_user(
            userEmailAddress = "user2@example.com",
            password = "testpass112233",
            userName = "Test Name 1",
            userPhoneNumber = "+60123456634",
            userUsername = "user2username"
        )

        self.user.following.add(other_user, other_user1)
        url = reverse("user:following_list", kwargs={"user_id": self.user.id})
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),2)
        self.assertEqual(res.data[0]["userUsername"], other_user.userUsername)
        self.assertEqual(res.data[1]["userUsername"], other_user1.userUsername)

    def test_retrieving_user_followers_following_counts(self):
        """Test retrieving a user with followers and following count"""
        other_user = create_user(
            userEmailAddress = "user1@example.com",
            password = "testpass112233",
            userName = "Test Name",
            userPhoneNumber = "+60123456543",
            userUsername = "user1username"
        )
        self.user.following.add(other_user)
        url = detail_url(other_user.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["userFollowerCount"], 1)
        self.assertEqual(res.data["userFollowingCount"],0)

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["userFollowerCount"], 0)
        self.assertEqual(res.data["userFollowingCount"],1)

    def test_retrieving_user_friends(self):
        """Test retrieving a user friends list"""
        other_user = create_user(
            userEmailAddress = "user1@example.com",
            password = "testpass112233",
            userName = "Test Name",
            userPhoneNumber = "+60123456543",
            userUsername = "user1username"
        )
        self.user.following.add(other_user)
        other_user.following.add(self.user)

        url = reverse("user:friends_list", kwargs={"user_id": self.user.id})
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]["userUsername"], other_user.userUsername)








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
        """Test uploading an image to a user profile"""
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

    def test_replace_image(self):
        """Test replacing an image on a user profile deletes the old one """
        # upload the first image
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

        # save the path of the first uplaoded image
        old_image_path = self.user.userProfilePictureUrl.path

        #upload the second image
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

        #Check the first image has been deleted
        self.assertFalse(os.path.exists(old_image_path))


    def test_upload_cover_picture(self):
        """Test uploading a cover picture to a user profile"""
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10,10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {"userCoverPictureUrl": image_file}
            res = self.client.post(COVER_PICTURE_URL, payload, format="multipart")

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("userCoverPictureUrl", res.data)
        self.assertTrue(os.path.exists(self.user.userCoverPictureUrl.path))

    def test_replace_cover_picture(self):
        """Test replacing a cover picture on a user profile deletes the old one """
        # upload the first image
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10,10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {"userCoverPictureUrl": image_file}
            res = self.client.post(COVER_PICTURE_URL, payload, format="multipart")

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("userCoverPictureUrl", res.data)
        self.assertTrue(os.path.exists(self.user.userCoverPictureUrl.path))

        # save the path of the first uplaoded image
        old_image_path = self.user.userCoverPictureUrl.path

        #upload the second image
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10,10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {"userCoverPictureUrl": image_file}
            res = self.client.post(COVER_PICTURE_URL, payload, format="multipart")

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("userCoverPictureUrl", res.data)
        self.assertTrue(os.path.exists(self.user.userCoverPictureUrl.path))

        self.assertFalse(os.path.exists(old_image_path))







