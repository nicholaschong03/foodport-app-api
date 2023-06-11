"""
Tests for menu APIs
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import MenuItem
from menu.serializers import MenuItemSerializer, MenuItemDetailSerializer

MY_MENU_URL = reverse("menu:my-menu-list")
MENU_LIST_URL = reverse("menu:menu-list")
ALL_MENU_LIST = reverse("menu:retrieve-nearby-menu")
FOOD_MENU_LIST = reverse("menu:retrieve-food-menu")
DRINK_MENU_LIST = reverse("menu:retrieve-drink-menu")
DESSERT_MENU_LIST=reverse("menu:retrieve-dessert-menu")

def detail_url(menu_id):
    """Create and return a users' own menu detail URL"""
    return reverse("menu:my-menu-detail", args=[menu_id])

def specific_menu_url(menu_id):
    """Create and return a specific menu URL"""
    return reverse("menu:retrieve-menu", args=[menu_id])

def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create_user(**params)

def create_menu(user, **params):
    """Create and retrun sample menu"""
    defaults = {
        "name": "Tom Yam",
        "price": 10.50,
        "category": "Food",
    }
    defaults.update(params)
    menu = MenuItem.objects.create(user=user, **defaults)
    return menu

class PublicMenuAPITest(TestCase):
    """Test unauthenticated user to create a menu"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(MY_MENU_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMenuAPITests(TestCase):
    """Test authenticated API request"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(userEmailAddress="user@example.com", password="test123", userUsername="username03")
        self.client.force_authenticate(self.user)

    def test_retrieve_menu(self):
        """Test retrieving a list of menu"""
        create_menu(user=self.user)
        create_menu(user=self.user)
        res = self.client.get(MY_MENU_URL)

        menu = MenuItem.objects.all().order_by("-id")
        serializer = MenuItemSerializer(menu, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_menu_list_limited_to_user(self):
        """Test list of menu is limited to authenticated user."""
        other_user = create_user(
        userEmailAddress="other@example.com",
        password="password123",
        userPhoneNumber="+60123456789",
        userUsername = "otherusername"
        )
        create_menu(user=other_user)
        create_menu(user=self.user)

        res = self.client.get(MY_MENU_URL)

        menu = MenuItem.objects.filter(user=self.user)
        serializer = MenuItemSerializer(menu, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_menu_detail(self):
        """Test get menu detail"""
        menu = create_menu(user=self.user)

        url = detail_url(menu.id)
        res = self.client.get(url)

        serializer = MenuItemDetailSerializer(menu)
        self.assertEqual(res.data, serializer.data)

    def test_create_(self):
        """Test creating a menu"""
        payload = {
            "name": "Tom Yam",
            "price": 10.50,
            "category": "Food",
        }
        res = self.client.post(MY_MENU_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        menu = MenuItem.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(menu, k), v)
        self.assertEqual(menu.user, self.user)

    def test_partial_update(self):
        """Tet partial update of a menu"""
        original_menuName = "Menu A"
        menu = create_menu(
            user = self.user,
            name = original_menuName,
            price = 12.50,
            category = "Food",
        )

        payload = {"name": "menu B"}
        url = detail_url(menu.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        menu.refresh_from_db()
        self.assertEqual(menu.name, payload["name"])
        self.assertEqual(menu.price, 12.50)
        self.assertEqual(menu.category, "Food")


    def test_full_update(self):
        """Test full update of menu"""
        menu = create_menu(
            user=self.user,
            name = "Nasi Lemak",
            price = 12.50,
            category = "Drink",


        )

        paylaod = {
            "name": "Tom Yam",
            "price": 10.50,
            "category": "Food",
        }
        url = detail_url(menu.id)
        res = self.client.put(url, paylaod)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        menu.refresh_from_db()
        for k, v in paylaod.items():
            self.assertEqual(getattr(menu, k), v)
        self.assertEqual(menu.user, self.user)

    # def test_update_user_returns_error(self):
    #     """Test changing the seller user results in an error"""
    #     new_user = create_user(userEmailAddress="user2@example.com",
    #                            password="test123",
    #                            userPhoneNumber="0123456843",
    #                            userUsername = "username1")
    #     menu = create_menu(user=self.user)

    #     payload = {"user": new_user.id}
    #     url = detail_url(menu.id)
    #     res = self.client.patch(url, payload)

    #     self.assertNotEqual(res.status_code, status.HTTP_200_OK)

    #     menu.refresh_from_db()
    #     self.assertEqual(menu.user, self.user)

    def test_delete_menu(self):
        """Test deleting a menu successful"""
        menu = create_menu(user=self.user)

        url = detail_url(menu.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MenuItem.objects.filter(id=menu.id).exists())

    def test_post_other_users_menu_error(self):
        """Test trying to delete another users menu gives error"""
        new_user = create_user(userEmailAddress="user2@example.com",
                               password="test123",
                               userPhoneNumber="0123456843",
                               userUsername = "username1")
        menu = create_menu(user=new_user)
        url = detail_url(menu.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(MenuItem.objects.filter(id=menu.id).exists())

    def test_user_list_search(self):
        """Test searching for a menu"""
        new_user = create_user(userEmailAddress="user2@example.com",
                                password="test123",
                                userPhoneNumber="0123456843",
                                userUsername = "username1")
        menu = create_menu(user=new_user)
        res = self.client.get(MENU_LIST_URL, {"search": "Tom Yam"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]),1)
        self.assertEqual(res.data["results"][0]["name"], menu.name)

    def test_retrieve_a_specific_menu(self):
        """Test get menu detail"""
        other_user = create_user(
        userEmailAddress="other@example.com",
        password="password123",
        userPhoneNumber="+60123456789",
        userUsername = "otherusername"
        )
        menu = create_menu(user=other_user)

        url = specific_menu_url(menu.id)
        res = self.client.get(url)

        serializer = MenuItemDetailSerializer(menu)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_all_existing_menus(self):
        """Test retrieving all existing menus"""
        # create users
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

        # create menus
        create_menu(user=user1)
        create_menu(user=user2)

        res = self.client.get(MENU_LIST_URL)

        # check status code
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # check that all menus are returned
        self.assertEqual(len(res.data["results"]), 2)

    def test_retrieve_menus_category_food(self):
        """Test retrieving menus where category is 'Food'"""
        # create users
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

        # create menus with category "Food"
        create_menu(user=user1, category="Food")
        create_menu(user=user2, category="Food")

        # create a menu with different category
        create_menu(user=user2, category="Drink")

        # perform get request with filter on category="Food"
        res = self.client.get(FOOD_MENU_LIST, {"category": "Food"})

        # check status code
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # check that only menus with category "Food" are returned
        self.assertEqual(len(res.data), 2)





