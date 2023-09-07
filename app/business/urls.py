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

]


