"""
URL mappings for the sellers api
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from seller import views

router = DefaultRouter()
router.register("sellers/user", views.SellerViewset, basename="my-sellers")

app_name = "seller"

urlpatterns = [
    path("", include(router.urls)),
    path("sellers/venture-day/", views.SellerListView.as_view(), name = 'seller_list'),
    path('sellers/<int:id>/', views.RetrieveSellerView.as_view(), name='retrieve_seller'),
    path("sellers/", views.AllSellersListView.as_view(), name="retrieve_all_seller"),
    path("seller/analytic/interest/total-post-like/<int:sellerId>/<str:startDateTime>/<str:endDateTime>/", views.LikePercentageChangeView.as_view(), name="analytic_total_post_like"),
    path("seller/analytic/interest/interest-performance/<int:sellerId>/<str:startDateTime>/<str:endDateTime>/", views.DailyCumulativePostLikesView.as_view(), name="analytic_interest_performance"),

]


