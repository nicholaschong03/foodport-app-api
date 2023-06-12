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
    path("menu-item/venture-day/", views.MenuItemListView.as_view(), name = 'retrieve-filter-menu'),
    path("menu-item/<int:id>/", views.RetrieveMenuItemView.as_view(), name='retrieve-menu'),
    path("menu-item/explore/nearby/", views.MenuItemListView.as_view(), name = "menu-list"),
    path("menu-item/explore/trending/", views.MenuItemListView.as_view(), name = "menu-list"),
    path("menu-item/venture-day/trending/", views.MenuItemListView.as_view(), name="menu-list"),
    # path("menu-item/venture-day/food/", views.Menu.as_view(), name="retrieve-food-menu"),
    # path("menu-item/venture-day/drinks/", views.DrinkMenuItemListView.as_view(), name="retrieve-drink-menu"),
    # path("menu-item/venture-day/desserts/", views.DessertMenuItemListView.as_view(), name="retrieve-dessert-menu"),

]