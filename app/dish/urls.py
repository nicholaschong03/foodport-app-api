""""
URLs mapping for dish api
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from dish import views

router = DefaultRouter()
router.register("dishes", views.DishViewset)

app_name = "dish"

urlpatterns = [
    path("", include(router.urls)),
]
