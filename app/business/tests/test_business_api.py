"""
Tests for business APIs
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Business
from business.serializers import BusinessSerializer, BusinessDetailSerializer

MY_BUSINESSES_URL = reverse("business:my-businesses-list")
BUSINESS_LIST_URL = reverse("business:business_list")


def detail_url(business_id):
    """Create and return a business detail URL"""
    return reverse("business:my-businesses-detail", args=[business_id])


def specific_business_url(business_id):
    """Create and return a specific business URL"""
    return reverse("business:retrieve_business", args=[business_id])


def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create_user(**params)


def create_business(user, **params):
    """Create adn retrun sample businesses"""
    defaults = {
        "businessName": "sample name",
        "businessOperatingLocation": "Kuala Lumpur",
        "businessSafeFood": True,
        "businessVerified": False,
        "businessHalal": True
    }
    defaults.update(params)
    business = Business.objects.create(user=user, **defaults)
    return business


class PublicbusinessAPITest(TestCase):
    """Test unauthenticated user to create a business profile"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(MY_BUSINESSES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatebusinessPageAPITest(TestCase):
    """Test creating a business page with authenticated user"""


class PrivatebusinessAPITests(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            userEmailAddress="user@example.com", password="test123", userUsername="username03")
        self.client.force_authenticate(self.user)

    def test_retrieve_business(self):
        """Test retrieving a list of businesses"""
        create_business(user=self.user)
        create_business(user=self.user)
        res = self.client.get(MY_BUSINESSES_URL)

        businesses = Business.objects.all().order_by("-id")
        serializer = BusinessSerializer(businesses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_business_list_limited_to_user(self):
        """Test list of businesss is limited to authenticated user."""
        other_user = create_user(
            userEmailAddress="other@example.com",
            password="password123",
            userPhoneNumber="+60123456789",
            userUsername="otherusername"
        )
        create_business(user=other_user)
        create_business(user=self.user)

        res = self.client.get(MY_BUSINESSES_URL)

        businesss = Business.objects.filter(user=self.user)
        serializer = BusinessSerializer(businesss, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_business_detail(self):
        """Test get business detail"""
        business = create_business(user=self.user)

        url = detail_url(business.id)
        res = self.client.get(url)

        serializer = BusinessDetailSerializer(business)
        self.assertEqual(res.data, serializer.data)

    def test_create_business(self):
        """Test creating a business"""
        payload = {
            "businessName": "Restaurant Alex",
            # "businessOperatingLocation": "Selangor",
            "businessSafeFood": False,
            "businessVerified": False,
            "businessHalal": True
        }
        res = self.client.post(MY_BUSINESSES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        business = Business.objects.get(id=res.data['businessId'])
        for k, v in payload.items():
            self.assertEqual(getattr(business, k), v)
        self.assertEqual(business.user, self.user)

    def test_partial_update(self):
        """Tet partial update of a business"""
        original_businessName = "business A"
        business = create_business(
            user=self.user,
            businessName=original_businessName,
            businessOperatingLocation="Selangor",
            businessSafeFood=True,
            businessVerified=True,
            businessHalal=True,

        )

        payload = {"businessName": "business B"}
        url = detail_url(business.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        business.refresh_from_db()
        self.assertEqual(business.businessName, payload["businessName"])
        self.assertEqual(business.businessOperatingLocation, "Selangor")
        self.assertTrue(business.businessSafeFood)
        self.assertTrue(business.businessVerified)
        self.assertTrue(business.businessHalal)

    def test_full_update(self):
        """Test full update of business"""
        business = create_business(
            user=self.user,
            businessName="sample business name",
            # businessOperatingLocation = "Penang",
            businessSafeFood=True,
            businessVerified=True,
            businessHalal=True,

        )

        paylaod = {
            "businessName": "new business name",
            # "businessOperatingLocation" : "Kedah",
            "businessSafeFood": False,
            "businessVerified": False,
            "businessHalal": False
        }
        url = detail_url(business.id)
        res = self.client.put(url, paylaod)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        business.refresh_from_db()
        for k, v in paylaod.items():
            self.assertEqual(getattr(business, k), v)
        self.assertEqual(business.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the business user results in an error"""
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername="username1")
        business = create_business(user=self.user)

        payload = {"user": new_user.id}
        url = detail_url(business.id)
        self.client.patch(url, payload)

        business.refresh_from_db()
        self.assertEqual(business.user, self.user)

    def test_delete_business(self):
        """Test deleting a business successful"""
        business = create_business(user=self.user)

        url = detail_url(business.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Business.objects.filter(id=business.id).exists())

    def test_post_other_users_business_error(self):
        """Test trying to delete another users business gives error"""
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername="username1")
        business = create_business(user=new_user)
        url = detail_url(business.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Business.objects.filter(id=business.id).exists())

    def test_user_list_search(self):
        """Test searching for a business"""
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername="username1")
        business = create_business(user=new_user)
        res = self.client.get(BUSINESS_LIST_URL, {"search": "sample name"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]
                         ["businessName"], business.businessName)

    def test_retrieve_a_specific_business(self):
        """Test get business detail"""
        other_user = create_user(
            userEmailAddress="other@example.com",
            password="password123",
            userPhoneNumber="+60123456789",
            userUsername="otherusername"
        )
        business = create_business(user=other_user)

        url = specific_business_url(business.id)
        res = self.client.get(url)

        serializer = BusinessDetailSerializer(business)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_all_existing_businesss(self):
        """Test retrieving all businesss"""
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

        # create businesss
        create_business(user=user1)
        create_business(user=user2)

        res = self.client.get(reverse("business:retrieve_all_business"))

        # check status code
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # check that all businesss are returned
        self.assertEqual(len(res.data), 2)

    def test_follow_business(self):
        """Test following a business"""
        user1 = create_user(
            userEmailAddress="user1@example.com",
            password="test123",
            userPhoneNumber="0123456843",
            userUsername="username1"
        )

        business = create_business(user=user1)
        url = reverse("business:follow_business", args=[business.id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "followed")
        self.assertTrue(self.user in business.followers.all())

    def test_unfollow_business(self):
        """Test following a business"""
        user1 = create_user(
            userEmailAddress="user1@example.com",
            password="test123",
            userPhoneNumber="0123456843",
            userUsername="username1"
        )

        business = create_business(user=user1)
        business.followers.add(self.user)
        url = reverse("business:follow_business", args=[business.id])
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "unfollowed")
        self.assertFalse(self.user in business.followers.all())

    def test_retrieve_business_followers(self):
        """Test retrieving a list of business followers"""
        user1 = create_user(
            userEmailAddress="user1@example.com",
            password="test123",
            userPhoneNumber="0123456843",
            userUsername="username1"
        )

        user2 = create_user(
            userEmailAddress = "user2@example.com",
            password = "test123",
            userPhoneNumber = "0123456789",
            userUsername = "username2"
        )

        business = create_business(user=user1)
        business.followers.add(user1)
        business.followers.add(user2)
        url = reverse("business:followers_list", args=[business.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),2)

    def test_retrieve_business_followings(self):
        """Test retrieving a business following list"""
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

        business = create_business(user=other_user)
        busienss2 = create_business(user=other_user1)
        business.followers.add(other_user)
        busienss2.followers.add(other_user)
        url = reverse("business:following_businesses_list", kwargs={"user_id": other_user.id})
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)


