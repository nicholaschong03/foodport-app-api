"""
URL mappings for the sellers api
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from business import views

router = DefaultRouter()
router.register("businesses/user", views.BusinessViewset, basename="my-businesses")

app_name = "business"

urlpatterns = [
    path("", include(router.urls)),
    path("businesses/", views.BusinessListView.as_view(), name = 'business_list'),
    path('businesses/<int:id>/', views.RetrieveBusinessView.as_view(), name='retrieve_business'),
    path("businesses/venture-day/", views.AllBusinessesListView.as_view(), name="retrieve_all_business"),
    path("businesses/analytic/interest/total-post-like/<int:businessId>/<str:startDateTime>/<str:endDateTime>/", views.LikePercentageChangeView.as_view(), name="analytic_total_post_like"),
    path("businesses/analytic/interest/interest-performance/<int:businessId>/<str:startDateTime>/<str:endDateTime>/", views.DailyCumulativePostLikesView.as_view(), name="analytic_interest_performance"),
    path("businesses/follow/<int:business_id>/", views.FollowBusinessView.as_view(), name="follow_business"),
    path("businesses/<int:business_id>/followers/", views.BusinessFollowersListView.as_view(), name="followers_list"),
    path("user/<int:user_id>/following-businesses/", views.FollowingBusinessesListView.as_view(),name="following_businesses_list")


]


