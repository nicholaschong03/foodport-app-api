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

from core.models import Post,PostLike, PostSave

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
    defaults.update(params)
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
        self.user = create_user(
            userEmailAddress="user@example.com", password="test123", userUsername="username03")
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

    def test_retrieve_followers_latest_posts(self):
        """Test retrieving followers latest posts"""
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername="username1")

        new_user2 = create_user(userEmailAddress="user3@example.com",
                                password="test123",
                                userPhoneNumber="0123436843",
                                userUsername="username3")

        new_user3 = create_user(userEmailAddress="user4@example.com",
                                password="test123",
                                userPhoneNumber="0123456813",
                                userUsername="username4")

        self.user.following.add(new_user, new_user2)
        post1 = create_post(user=new_user)
        post2 = create_post(user=new_user2)
        post3 = create_post(user=new_user2)
        post4 = create_post(user=new_user3)

        url = reverse("post:following-post")
        res = self.client.get(url)
        # print(res.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)

        self.assertEqual(res.data[0]["postId"], post3.id)
        self.assertEqual(res.data[1]["postId"], post2.id)
        self.assertEqual(res.data[2]["postId"], post1.id)
        self.assertNotIn(post4, res.data)

    def test_like_post(self):
        """Test if user is able to like a post"""
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername="username1")
        post = create_post(user=new_user)
        url = reverse("post:like-post", kwargs={"post_id": post.id})
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        latest_postLike = PostLike.objects.filter(post=post, user=self.user).order_by("-likeDateTime").first()
        if latest_postLike:
            self.assertTrue(latest_postLike.isActive)
        else:
            self.fail("PostLike object not found")

    def test_unlike_post(self):
        """Test if user is able to unlike a post"""
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername="username1")
        post = create_post(user=new_user)
        PostLike.objects.create(user=self.user, post=post, isActive=True)
        url = reverse("post:like-post", kwargs={"post_id": post.id})
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        latest_postLike = PostLike.objects.filter(post=post, user=self.user).order_by("-likeDateTime").first()
        self.assertFalse(latest_postLike.isActive)


    def test_retrieve_post_likes(self):
        """Test retrieving a list of user who like a post"""
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

        post = create_post(user=self.user)
        PostLike.objects.create(user=other_user, post=post, isActive=True)
        PostLike.objects.create(user=other_user1, post=post, isActive=True)
        url = reverse("post:post-liked-users-list", kwargs={"post_id": post.id})
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),2)

        usernames_in_response = [user["userUsername"] for user in res.data]
        self.assertIn(other_user.userUsername, usernames_in_response)
        self.assertIn(other_user1.userUsername, usernames_in_response)

    def test_retrieve_liked_posts(self):
        """Test retrieving a list of posts liked by a user"""
        new_user = create_user(
            userEmailAddress = "user2@example.com",
            password = "test123",
            userPhoneNumber = "0123456789",
            userUsername= "username1"
        )

        post1 = create_post(user=new_user)
        post2 = create_post(user=new_user)

        PostLike.objects.create(user=self.user, post=post1, isActive=True)
        PostLike.objects.create(user=self.user, post=post2, isActive=True)

        url = reverse("post:liked-post-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        post_ids_in_response = [post["postId"] for post in res.data]
        self.assertIn(post1.id, post_ids_in_response)
        self.assertIn(post2.id, post_ids_in_response)

    def test_retrieve_post_like_list(self):
        """Test retrieving a list of postLikes for a user"""
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

        post = create_post(user=self.user)
        PostLike.objects.create(user=other_user, post=post, isActive=True)
        PostLike.objects.create(user=other_user1, post=post, isActive=True)
        url = reverse("post:postlike-list", kwargs={"post_id": post.id})
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),2)
        self.assertIn(res.data[0]["userId"], [other_user.id, other_user1.id])
        self.assertIn(res.data[1]["userId"], [other_user.id, other_user1.id])

    def test_save_unsave_post(self):
        """Test saving and unsaving a post"""
        user1 = create_user(userEmailAddress="user1@example.com",
                               password = "test123",
                               userPhoneNumber = "0123456834",
                               userUsername="username1")
        post = create_post(user=user1)
        url = reverse("post:save-post", kwargs={"post_id": post.id})

        #save the post
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(PostSave.objects.filter(user=self.user, post=post, postIsSaved=True).exists())

        #unsave the post
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(PostSave.objects.filter(user=self.user, post=post, postIsSaved=True).exists())


    def test_list_saved_posts(self):
        """Testing listing saved posts"""
        user1 = create_user(userEmailAddress="user1@example.com",
                            password = "test123",
                            userPhoneNumber = "012345678733",
                            userUsername = "username1")
        post1 = create_post(user=user1)
        post2 = create_post(user=user1)

        PostSave.objects.create(user=self.user, post=post1, postIsSaved=True)
        PostSave.objects.create(user=self.user, post=post2, postIsSaved=True)

        url = reverse("post:saved-post-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        post_ids_in_response = [post["postId"] for post in res.data]
        self.assertIn(post1.id, post_ids_in_response)
        self.assertIn(post2.id, post_ids_in_response)



    def test_retrieve_menus_category_food(self):
        """Test retrieving menus where category is 'Food'"""
        # create users
        user1 = create_user(
            userEmailAddress="user1@example.com",
            password="test123",
            userPhoneNumber="0123456843",
            userUsername="username1"
        )
        user2 = create_user(
            userEmailAddress="user2@example.com",
            password="password123",
            userPhoneNumber="+60123456789",
            userUsername="username2"
        )

        create_post(
            user=user1,
            postReview="very delicious",
            postRatingDelicious=5,
            postRatingEatAgain=3,
            postRatingWorthIt=2,
            menuItemId=1

        )

        create_post(
            user=user2,
            postReview="very delicious",
            postRatingDelicious=5,
            postRatingEatAgain=3,
            postRatingWorthIt=2,
            menuItemId=1

        )


        create_post(
            user=self.user,
            postReview="very delicious",
            postRatingDelicious=5,
            postRatingEatAgain=3,
            postRatingWorthIt=2,
            menuItemId=2

        )

        # perform get request with filter on menuItemId= 1
        url = reverse("post:for-you-post-feed")
        res = self.client.get(url, {"menuItemId": 1})



        self.assertEqual(res.status_code, status.HTTP_200_OK)


        self.assertEqual(len(res.data['results']), 2)

    def test_return_rating_review(self):

        post1 = create_post(
            user=self.user,
            postReview="fucking bad",
            postRatingDelicious=4.5,
            postRatingEatAgain=4.2,
            postRatingWorthIt=4.8,
            menuItemId=1

        )

        post2 = create_post(
            user=self.user,
            postReview="very tasty",
            postRatingDelicious=3.8,
            postRatingEatAgain=4.5,
            postRatingWorthIt=4.0,
            menuItemId=1

        )


        post3 = create_post(
            user=self.user,
            postReview="very delicious",
            postRatingDelicious=4.2,
            postRatingEatAgain=4.0,
            postRatingWorthIt=4.3,
            menuItemId=2

        )

        url = reverse("post:review-rating-post")

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer_data = res.data
        self.assertEqual(len(serializer_data["results"]), 3)








    def test_post_list_limited_to_user(self):
        """Test list of posts is limited to authenticated user."""
        other_user = create_user(
            userEmailAddress="other@example.com",
            password="password123",
            userPhoneNumber="+60123456789",
            userUsername="otherusername"
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
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername="username1")
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
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername="username1")
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
            userEmailAddress="user@example.com",
            password="password123",
            userUsername="example username"
        )
        self.client.force_authenticate(self.user)
        self.post = create_post(user=self.user)

    def tearDown(self):
        self.post.postPhotoUrl.delete()

    def test_upload_image(self):
        """Test uploading an image to a post"""
        url = image_upload_url(self.post.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
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
