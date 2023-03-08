"""
Tests for posts APIs.
"""
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Post

from post.serializers import PostSerializer, PostDetailSerializer

POSTS_URL = reverse("post:post-list")


def detail_url(post_id):
    """Create and return a post detail URL"""
    return reverse("post:post-detail", args=[post_id])

def image_upload_url(post_id):
    """Create and return an image upload URL"""
    return reverse("post:post-upload-image", args=[post_id])

def create_post(user, **params):
    """Create and return a sample posts"""
    defaults = {
        "postReview": "sample post review",
        "postRatingDelicious": 5,
        "postRatingEatAgain": 3,
        "postRatingWorthIt": 2,
    }
    post = Post.objects.create(user=user, **defaults)
    return post


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicPostApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(POSTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePostApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="test123", username="username03")
        self.client.force_authenticate(self.user)

    def test_retrieve_posts(self):
        """Test retrieving a list of posts"""
        create_post(user=self.user)
        create_post(user=self.user)
        res = self.client.get(POSTS_URL)

        posts = Post.objects.all().order_by("-id")
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_post_list_limited_to_user(self):
        """Test list of posts is limited to authenticated user."""
        other_user = create_user(
            email="other@example.com",
            password="password123",
            phone_num="+60123456789",
            username = "otherusername"
        )
        create_post(user=other_user)
        create_post(user=self.user)

        res = self.client.get(POSTS_URL)

        posts = Post.objects.filter(user=self.user)
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_post_detail(self):
        """Test get post detail"""
        post = create_post(user=self.user)

        url = detail_url(post.id)
        res = self.client.get(url)

        serializer = PostDetailSerializer(post)
        self.assertEqual(res.data, serializer.data)

    def test_create_post(self):
        """Test creating a post"""
        payload = {
            "postReview": "sample post review",
            "postRatingDelicious": 5,
            "postRatingEatAgain": 3,
            "postRatingWorthIt": 2,
        }
        res = self.client.post(POSTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(id=res.data['postId'])
        for k, v in payload.items():
            self.assertEqual(getattr(post, k), v)
        self.assertEqual(post.user, self.user)

    def test_partial_update(self):
        """Tet partial update of a post"""
        original_postReview = "this is delicious"
        post = create_post(
            user=self.user,
            postReview=original_postReview,
            postRatingDelicious=5,
            postRatingEatAgain=3,
            postRatingWorthIt=2

        )

        payload = {"postReview": "This is bad"}
        url = detail_url(post.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.postReview, payload["postReview"])
        self.assertEqual(post.postRatingDelicious, 5)
        self.assertEqual(post.postRatingEatAgain, 3)
        self.assertEqual(post.postRatingWorthIt, 2)
        self.assertEqual(post.user, self.user)

    def test_full_update(self):
        """Test full update of post"""
        post = create_post(
            user=self.user,
            postReview="very delicious",
            postRatingDelicious=5,
            postRatingEatAgain=3,
            postRatingWorthIt=2

        )

        paylaod = {
            "postReview": "updated post review",
            "postRatingDelicious": 1,
            "postRatingEatAgain": 1,
            "postRatingWorthIt": 1,
        }
        url = detail_url(post.id)
        res = self.client.put(url, paylaod)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        for k, v in paylaod.items():
            self.assertEqual(getattr(post, k), v)
        self.assertEqual(post.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the post user results in an error"""
        new_user = create_user(email="user2@example.com",
                               password="test123",
                               phone_num="0123456843",
                               username = "username1")
        post = create_post(user=self.user)

        payload = {"user": new_user.id}
        url = detail_url(post.id)
        self.client.patch(url, payload)

        post.refresh_from_db()
        self.assertEqual(post.user, self.user)

    def test_delete_post(self):
        """Test deleting a post successful"""
        post = create_post(user=self.user)

        url = detail_url(post.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    def test_post_other_users_post_error(self):
        """Test trying to delete another users post gives error"""
        new_user = create_user(email="user2@example.com",
                               password="test123",
                               phone_num="0123456843",
                               username = "username1")
        post = create_post(user=new_user)
        url = detail_url(post.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Post.objects.filter(id=post.id).exists())


class ImageUploadTests(TestCase):
    """Test for the image upload API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password = "password123",
            username = "example username"
        )
        self.client.force_authenticate(self.user)
        self.post = create_post(user=self.user)

    def tearDown(self):
        self.post.postPhotoUrl.delete()


    def test_upload_image(self):
        """Test uploading an image to a post"""
        url = image_upload_url(self.post.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10,10))
            img.save(image_file, format="JPEG")
            image_file.seek(0)
            payload = {"postPhotoUrl": image_file}
            res = self.client.post(url, payload, format="multipart")

        self.post.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("postPhotoUrl", res.data)
        self.assertTrue(os.path.exists(self.post.postPhotoUrl.path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image"""
        url = image_upload_url(self.post.id)
        payload = {"postPhotoUrl": "notanimage"}
        res = self.client.post(url, payload, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)