"""
URL mappings for the sellers api
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from seller import views

router = DefaultRouter()
router.register("sellers", views.SellerViewset)

app_name = "seller"

urlpatterns = [
    path("", include(router.urls)),
]


