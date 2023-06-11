"""
Tests for seller APIs
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Seller
from seller.serializers import SellerSerializer, SellerDetailSerializer

MY_SELLERS_URL = reverse("seller:my-sellers-list")
SELLER_LIST_URL = reverse("seller:seller_list")

def detail_url(seller_id):
    """Create and return a seller detail URL"""
    return reverse("seller:my-sellers-detail", args=[seller_id])

def specific_seller_url(seller_id):
    """Create and return a specific seller URL"""
    return reverse("seller:retrieve_seller", args=[seller_id])

def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create_user(**params)

def create_seller(user, **params):
    """Create adn retrun sample sellers"""
    defaults = {
        "sellerBusinessName": "sample name",
        "sellerOperatingLocation": "Kuala Lumpur",
        "sellerSafeFood": True,
        "sellerVerified" : False,
        "sellerHalal": True
    }
    defaults.update(params)
    seller = Seller.objects.create(user=user, **defaults)
    return seller

class PublicSellerAPITest(TestCase):
    """Test unauthenticated user to create a seller profile"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(MY_SELLERS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateSellerPageAPITest(TestCase):
    """Test creating a seller page with authenticated user"""

class PrivateSellerAPITests(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(userEmailAddress="user@example.com", password="test123", userUsername="username03")
        self.client.force_authenticate(self.user)

    def test_retrieve_seller(self):
        """Test retrieving a list of sellers"""
        create_seller(user=self.user)
        create_seller(user=self.user)
        res = self.client.get(MY_SELLERS_URL)

        sellers = Seller.objects.all().order_by("-id")
        serializer = SellerSerializer(sellers, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_seller_list_limited_to_user(self):
        """Test list of sellers is limited to authenticated user."""
        other_user = create_user(
        userEmailAddress="other@example.com",
        password="password123",
        userPhoneNumber="+60123456789",
        userUsername = "otherusername"
        )
        create_seller(user=other_user)
        create_seller(user=self.user)

        res = self.client.get(MY_SELLERS_URL)

        sellers = Seller.objects.filter(user=self.user)
        serializer = SellerSerializer(sellers, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_seller_detail(self):
        """Test get seller detail"""
        seller = create_seller(user=self.user)

        url = detail_url(seller.id)
        res = self.client.get(url)

        serializer = SellerDetailSerializer(seller)
        self.assertEqual(res.data, serializer.data)

    def test_create_seller(self):
        """Test creating a seller"""
        payload = {
            "sellerBusinessName": "Restaurant Alex",
            # "sellerOperatingLocation": "Selangor",
            "sellerSafeFood": False,
            "sellerVerified": False,
            "sellerHalal" : True
        }
        res = self.client.post(MY_SELLERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        seller = Seller.objects.get(id=res.data['sellerId'])
        for k, v in payload.items():
            self.assertEqual(getattr(seller, k), v)
        self.assertEqual(seller.user, self.user)

    def test_partial_update(self):
        """Tet partial update of a seller"""
        original_sellerName = "Seller A"
        seller = create_seller(
            user=self.user,
            sellerBusinessName=original_sellerName,
            sellerOperatingLocation = "Selangor",
            sellerSafeFood=True,
            sellerVerified = True,
            sellerHalal=True,

        )

        payload = {"sellerBusinessName": "Seller B"}
        url = detail_url(seller.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        seller.refresh_from_db()
        self.assertEqual(seller.sellerBusinessName, payload["sellerBusinessName"])
        self.assertEqual(seller.sellerOperatingLocation, "Selangor")
        self.assertTrue(seller.sellerSafeFood)
        self.assertTrue(seller.sellerVerified)
        self.assertTrue(seller.sellerHalal)


    def test_full_update(self):
        """Test full update of seller"""
        seller = create_seller(
            user=self.user,
            sellerBusinessName="sample seller name",
            # sellerOperatingLocation = "Penang",
            sellerSafeFood = True,
            sellerVerified = True,
            sellerHalal = True,

        )

        paylaod = {
            "sellerBusinessName": "new seller name",
            # "sellerOperatingLocation" : "Kedah",
            "sellerSafeFood" : False,
            "sellerVerified" : False,
            "sellerHalal" : False
        }
        url = detail_url(seller.id)
        res = self.client.put(url, paylaod)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        seller.refresh_from_db()
        for k, v in paylaod.items():
            self.assertEqual(getattr(seller, k), v)
        self.assertEqual(seller.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the seller user results in an error"""
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername = "username1")
        seller = create_seller(user=self.user)

        payload = {"user": new_user.id}
        url = detail_url(seller.id)
        self.client.patch(url, payload)

        seller.refresh_from_db()
        self.assertEqual(seller.user, self.user)

    def test_delete_seller(self):
        """Test deleting a seller successful"""
        seller = create_seller(user=self.user)

        url = detail_url(seller.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Seller.objects.filter(id=seller.id).exists())

    def test_post_other_users_seller_error(self):
        """Test trying to delete another users seller gives error"""
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername = "username1")
        seller = create_seller(user=new_user)
        url = detail_url(seller.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Seller.objects.filter(id=seller.id).exists())


    def test_user_list_search(self):
        """Test searching for a seller"""
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername = "username1")
        seller = create_seller(user=new_user)
        res = self.client.get(SELLER_LIST_URL, {"search": "sample name"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]),1)
        self.assertEqual(res.data["results"][0]["sellerBusinessName"], seller.sellerBusinessName)

    def test_retrieve_a_specific_seller(self):
        """Test get seller detail"""
        other_user = create_user(
        userEmailAddress="other@example.com",
        password="password123",
        userPhoneNumber="+60123456789",
        userUsername = "otherusername"
        )
        seller = create_seller(user=other_user)

        url = specific_seller_url(seller.id)
        res = self.client.get(url)

        serializer = SellerDetailSerializer(seller)
        self.assertEqual(res.data, serializer.data)


    def test_retrieve_all_existing_sellers(self):
        """Test retrieving all sellers"""
        user1 = create_user(
            userEmailAddress="user1@example.com",
            password="test123",
            userPhoneNumber="0123456843",
            userUsername = "username1"
        )
        user2 = create_user(
            userEmailAddress="user2@example.com",
            password="password123",
            userPhoneNumber="+60123456789",
            userUsername = "username2"
        )

        # create sellers
        create_seller(user=user1)
        create_seller(user=user2)

        res = self.client.get(reverse("seller:retrieve_all_seller"))

        # check status code
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # check that all sellers are returned
        self.assertEqual(len(res.data), 2)









