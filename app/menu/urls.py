""""
URLs mapping for dish api
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from menu import views

router = DefaultRouter()
router.register("menu-item/user", views.MenuItemViewset, basename= "my-menu")

app_name = "menu"

urlpatterns = [
    path("", include(router.urls)),
    path("menu-item/", views.MenuItemListView.as_view(), name = 'menu-list'),
    path("menu-item/<int:id>/", views.RetrieveMenuItemView.as_view(), name='retrieve-menu'),
    path("menu-item/explore/nearby/", views.AllMenuItemListView.as_view(), name = "retrieve-nearby-menu"),
    path("menu-item/explore/trending/", views.AllMenuItemListView.as_view(), name = "retrieve-trending-menu"),
    path("menu-item/venture-day/trending/", views.AllMenuItemListView.as_view(), name="retrieve-venture-day-menu"),
    path("menu-item/venture-day/food/", views.FoodMenuItemListView.as_view(), name="retrieve-food-menu"),
    path("menu-item/venture-day/drinks/", views.DrinkMenuItemListView.as_view(), name="retrieve-drink-menu"),
    path("menu-item/venture-day/desserts/", views.DessertMenuItemListView.as_view(), name="retrieve-dessert-menu"),

]