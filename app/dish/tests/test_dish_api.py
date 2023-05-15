"""
Tests for dish APIs
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Dish
from dish.serializers import DishSerializer, DishDetailSerializer

MY_DISHES_URL = reverse("dish:my-dishes-list")
DISHES_LIST_URL = reverse("dish:dish_list")

def detail_url(dish_id):
    """Create and return a users' own dish detail URL"""
    return reverse("dish:dish-detail", args=[dish_id])

def specific_dish_url(dish_id):
    """Create and return a specific dish URL"""
    return reverse("dish:retrieve_dish", args=[dish_id])

def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create_user(**params)

def create_dish(user, **params):
    """Create and retrun sample dish"""
    defaults = {
        "dishName": "Tom Yam",
        "dishPrice": 10.50,
        "dishMainIngredient": "Noodle",
        "dishIngredient" : "Chili",
        "dishNutrition": "Vitamin",
    }
    defaults.update(params)
    dish = Dish.objects.create(user=user, **defaults)
    return dish

class PublicDishAPITest(TestCase):
    """Test unauthenticated user to create a dish"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(MY_DISHES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateDishPageAPITest(TestCase):
    """Test creating a dish page with authenticated user"""

class PrivateDishAPITests(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(userEmailAddress="user@example.com", password="test123", userUsername="username03")
        self.client.force_authenticate(self.user)

    def test_retrieve_dish(self):
        """Test retrieving a list of dishes"""
        create_dish(user=self.user)
        create_dish(user=self.user)
        res = self.client.get(MY_DISHES_URL)

        dishes = Dish.objects.all().order_by("-id")
        serializer = DishSerializer(dishes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_dish_list_limited_to_user(self):
        """Test list of dishes is limited to authenticated user."""
        other_user = create_user(
        userEmailAddress="other@example.com",
        password="password123",
        userPhoneNumber="+60123456789",
        userUsername = "otherusername"
        )
        create_dish(user=other_user)
        create_dish(user=self.user)

        res = self.client.get(MY_DISHES_URL)

        dish = Dish.objects.filter(user=self.user)
        serializer = DishSerializer(dish, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_dish_detail(self):
        """Test get dish detail"""
        dish = create_dish(user=self.user)

        url = detail_url(dish.id)
        res = self.client.get(url)

        serializer = DishDetailSerializer(dish)
        self.assertEqual(res.data, serializer.data)

    def test_create_(self):
        """Test creating a dish"""
        payload = {
            "dishName": "Tom Yam",
            "dishPrice": 10.50,
            "dishMainIngredient": "Noodle",
            "dishIngredient" : "Chili",
            "dishNutrition": "Vitamin",
        }
        res = self.client.post(MY_DISHES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        dish = Dish.objects.get(id=res.data['dishId'])
        for k, v in payload.items():
            self.assertEqual(getattr(dish, k), v)
        self.assertEqual(dish.user, self.user)

    def test_partial_update(self):
        """Tet partial update of a dish"""
        original_dishName = "Dish A"
        dish = create_dish(
            user=self.user,
            dishName = original_dishName,
            dishPrice = 12.50,
            dishMainIngredient = "Rice",
            dishIngredient = "Bread",
            dishNutrition = "Vitamin A"
        )

        payload = {"dishName": "Dish B"}
        url = detail_url(dish.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        dish.refresh_from_db()
        self.assertEqual(dish.dishName, payload["dishName"])
        self.assertEqual(dish.dishPrice, 12.50)
        self.assertEqual(dish.dishMainIngredient, "Rice")
        self.assertEqual(dish.dishIngredient, "Bread")
        self.assertEqual(dish.dishNutrition, "Vitamin A")


    def test_full_update(self):
        """Test full update of dish"""
        dish = create_dish(
            user=self.user,
            dishName = "Nasi Lemak",
            dishPrice = 12.50,
            dishMainIngredient = "Rice",
            dishIngredient = "Bread",
            dishNutrition = "Vitamin A"

        )

        paylaod = {
            "dishName": "Tom Yam",
            "dishPrice": 10.50,
            "dishMainIngredient": "Noodle",
            "dishIngredient" : "Chili",
            "dishNutrition": "Vitamin",
        }
        url = detail_url(dish.id)
        res = self.client.put(url, paylaod)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        dish.refresh_from_db()
        for k, v in paylaod.items():
            self.assertEqual(getattr(dish, k), v)
        self.assertEqual(dish.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the seller user results in an error"""
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername = "username1")
        dish = create_dish(user=self.user)

        payload = {"user": new_user.id}
        url = detail_url(dish.id)
        res = self.client.patch(url, payload)

        self.assertNotEqual(res.status_code, status.HTTP_200_OK)

        dish.refresh_from_db()
        self.assertEqual(dish.user, self.user)

    def test_delete_dish(self):
        """Test deleting a dish successful"""
        dish = create_dish(user=self.user)

        url = detail_url(dish.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Dish.objects.filter(id=dish.id).exists())

    def test_post_other_users_dish_error(self):
        """Test trying to delete another users dish gives error"""
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername = "username1")
        dish = create_dish(user=new_user)
        url = detail_url(dish.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Dish.objects.filter(id=dish.id).exists())

    def test_user_list_search(self):
        """Test searching for a dish"""
        new_user = create_user(userEmailAddress="user2@example.com",
                                password="test123",
                                userPhoneNumber="0123456843",
                                userUsername = "username1")
        dish = create_dish(user=new_user)
        res = self.client.get(DISHES_LIST_URL, {"search": "Tom Yam"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]),1)
        self.assertEqual(res.data["results"][0]["dishName"], dish.dishName)

    def test_retrieve_a_specific_dish(self):
        """Test get dish detail"""
        other_user = create_user(
        userEmailAddress="other@example.com",
        password="password123",
        userPhoneNumber="+60123456789",
        userUsername = "otherusername"
        )
        dish = create_dish(user=other_user)

        url = specific_dish_url(dish.id)
        res = self.client.get(url)

        serializer = DishDetailSerializer(dish)
        self.assertEqual(res.data, serializer.data)







