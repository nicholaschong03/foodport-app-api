from rest_framework import viewsets, status, permissions, authentication, generics
from rest_framework.response import Response
from core.models import Business, Post, MenuItem, PostLike
from business.serializers import BusinessSerializer, BusinessDetailSerializer
from django.utils import timezone
from rest_framework import filters
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from django.db.models import Sum

from datetime import datetime, timedelta

from django.http import Http404

import random


class BusinessViewset(viewsets.ModelViewSet):
    """View for manage business APIs"""
    serializer_class = BusinessDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]
    queryset = Business.objects.all()

    def get_queryset(self):
        """Retrieve business for authenticated user"""
        user = self.request.user
        return self.queryset.filter(user=user).order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == "list":
            return BusinessSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        user = self.request.user
        ip_address = self.request.META.get("REMOTE_ADDR")

        business_info_contributor = {
            str(user.id): {
                "datetime": timezone.now().isoformat(),
                "IP_address": ip_address,
            }
        }
        serializer.save(
            user=user, businessInfoContributor=business_info_contributor)


class CustomBusinessPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class BusinessListView(generics.ListAPIView):
    queryset = Business.objects.all().order_by("businessName")
    serializer_class = BusinessSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["businessName"]
    pagination_class = CustomBusinessPagination


class RetrieveBusinessView(generics.RetrieveAPIView):
    """Retrieve a business"""
    serializer_class = BusinessDetailSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return a business"""
        try:
            business = Business.objects.get(id=self.kwargs["id"])
        except Business.DoesNotExist:
            raise Http404("Business not found")
        return business


class AllBusinessesListView(generics.ListAPIView):
    """Return a list of all existing menu items"""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BusinessSerializer

    def get_queryset(self):
        """Retrieve all the menu items"""
        return Business.objects.all().order_by("businessName")


class LikePercentageChangeView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, businessId, startDateTime, endDateTime, *args, **kwargs):
        try:
            business = Business.objects.get(id=businessId)
        except Business.DoesNotExist:
            return Response({"error": "Business not found"}, status=400)
        # Validate that the dates were provided
        if not startDateTime or not endDateTime:
            return Response({"error": "startDateTime and endDateTime query params are required"}, status=400)

        startDateTime = startDateTime.replace("_", " ").replace(
            "%20", " ").replace("%22", " ").replace("%3A", ":").strip('"').strip()
        endDateTime = endDateTime.replace("_", " ").replace("%20", " ").replace(
            "%22", " ").replace("%3A", ":").strip('"').strip()

        # Parse the datetime strings into datetime objects
        try:
            startDateTime = datetime.strptime(
                startDateTime, "%Y-%m-%dT%H:%M:%S.%fZ")
            endDateTime = datetime.strptime(
                endDateTime, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return Response({"error": "Invalid datetime format. Use ISO 8601 format 'YYYY-MM-DDTHH:MM:SS.sssZ'",
                             "startDate": startDateTime,
                             "businessId": businessId}, status=400,)

        # Get the business' menu items
        menu_items = MenuItem.objects.filter(id__in=business.menuItemId)

        # Get posts associated with business' menu items
        posts = Post.objects.filter(menuItemId__in=menu_items)

        # Calcualte likes at startDateTime and endDateTie
        start_likes = posts.filter(postPublishDateTime__lte=startDateTime).aggregate(
            sum=Sum("postLikeCount"))["sum"] or 0
        end_likes = posts.filter(postPublishDateTime__lte=endDateTime).aggregate(
            sum=Sum("postLikeCount"))["sum"] or 0

        # calculate trend direction and percentage change
        if start_likes == 0:
            if end_likes == 0:
                trend = "constant"
                percentage_change = 0
            else :
                trend = "up"
                percentage_change = 100
        else:
            if start_likes == end_likes:
                trend = "constant"
                percentage_change = 0
            elif start_likes < end_likes:
                trend = "up"
                percentage_change = ((end_likes - start_likes) / start_likes) * 100
            else:
                trend = "down"
                percentage_change = ((start_likes - end_likes) / start_likes) * 100

        # Return the result
        return Response({"amount": end_likes,
                         "trend": trend,
                         "trendPercentage": percentage_change})


class DailyCumulativePostLikesView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, businessId, startDateTime, endDateTime, *args, **kwargs):

        try:
            business = Business.objects.get(id=businessId)
        except Business.DoesNotExist:
            return Response({"error": "Business not found"}, status=400)

        # Validate that the dates were provided
        if not startDateTime or not endDateTime:
            return Response({"error": "startDateTime and endDateTime query params are required"}, status=400)

        startDateTime = startDateTime.replace("_", " ").replace(
            "%20", " ").replace("%22", " ").replace("%3A", ":").strip('"').strip()
        endDateTime = endDateTime.replace("_", " ").replace("%20", " ").replace(
            "%22", " ").replace("%3A", ":").strip('"').strip()

        # Parse the datetime strings into datetime objects
        try:
            startDateTime = datetime.strptime(
                startDateTime, "%Y-%m-%dT%H:%M:%S.%fZ")
            endDateTime = datetime.strptime(
                endDateTime, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return Response({"error": "Invalid datetime format. Use ISO 8601 format 'YYYY-MM-DDTHH:MM:SS.sssZ'",
                             "startDate": startDateTime,
                             "businessId": businessId}, status=400,)

        # Get the business' menu items
        menu_items = MenuItem.objects.filter(id__in=business.menuItemId)

        # Get posts associated with business' menu items
        posts = Post.objects.filter(menuItemId__in=menu_items)

        # Initialize the result list
        results = []

        delta = endDateTime - startDateTime
        if delta <= timedelta(hours=24):
            # If range is 24 hours, step is 2 hours
            step = timedelta(hours=2)
        elif delta <= timedelta(days=7):
            # If range is a week, step is one day
            step = timedelta(days=1)
        elif delta <= timedelta(days=31):
            # If range is a month, step is a week
            step = timedelta(days=7)
        elif delta <= timedelta(days=90):
            # If range is a quarter, step is one month
            step = timedelta(days=30)
        elif delta <= timedelta(days=365):
            # If range is a year, step is one month
            step = timedelta(days=30)
        else:
            # Default step is one day
            step = timedelta(days=1)

        day = startDateTime + step
        while day <= endDateTime:
            # Get the cumulative sum of likes for posts up to and including this day
            likes = PostLike.objects.filter(post__in = posts, likeDateTime__lte = day, isActive = True).count()
            likes -= PostLike.objects.filter(post__in = posts, likeDateTime__lte = day, isActive = False).count()
            save = random.randint(0, 100)
            share = random.randint(0, 100)
            comment = random.randint(0, 100)
            # Append the result to the results list
            results.append({"timestamp": day.isoformat(), "like": likes, "save": save, "share": share, "comment": comment})
            # Move to the next step
            day += step

        # Return the result
        return Response(results)
