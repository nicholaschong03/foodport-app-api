"""
URL mappings for the sellers api
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from seller import views

router = DefaultRouter()
router.register("my-sellers", views.SellerViewset, basename="my-sellers")

app_name = "seller"

urlpatterns = [
    path("", include(router.urls)),
    path("sellers/", views.SellerListView.as_view(), name = 'seller_list')
]


