""""
URLs mapping for dish api
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from dish import views

router = DefaultRouter()
router.register("dishes/user", views.DishViewset, basename= "my-dishes")

app_name = "dish"

urlpatterns = [
    path("", include(router.urls)),
    path("dishes/", views.DishListView.as_view(), name = 'dish_list'),
    path('dishes/<int:id>/', views.RetrieveDishView.as_view(), name='retrieve_dish'),

]
