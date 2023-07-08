from rest_framework import viewsets, status, permissions, authentication, generics
from rest_framework.response import Response
from core.models import Seller, Post, MenuItem
from seller.serializers import SellerSerializer, SellerDetailSerializer
from django.utils import timezone
from rest_framework import filters
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from django.db.models import Sum

from datetime import datetime, timedelta

from django.http import Http404


class SellerViewset(viewsets.ModelViewSet):
    """View for manage seller APIs"""
    serializer_class = SellerDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]
    queryset = Seller.objects.all()

    def get_queryset(self):
        """Retrieve sellers for authenticated user"""
        user = self.request.user
        return self.queryset.filter(user=user).order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == "list":
            return SellerSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        user = self.request.user
        ip_address = self.request.META.get("REMOTE_ADDR")

        seller_info_contributor = {
            str(user.id): {
                "datetime": timezone.now().isoformat(),
                "IP_address": ip_address,
            }
        }
        serializer.save(
            user=user, sellerInfoContributor=seller_info_contributor)


class CustomSellerPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class SellerListView(generics.ListAPIView):
    queryset = Seller.objects.all().order_by("sellerBusinessName")
    serializer_class = SellerSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["sellerBusinessName"]
    pagination_class = CustomSellerPagination


class RetrieveSellerView(generics.RetrieveAPIView):
    """Retrieve a seller"""
    serializer_class = SellerDetailSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return a seller"""
        try:
            seller = Seller.objects.get(id=self.kwargs["id"])
        except Seller.DoesNotExist:
            raise Http404("Seller not found")
        return seller


class AllSellersListView(generics.ListAPIView):
    """Return a list of all existing menu items"""
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SellerSerializer

    def get_queryset(self):
        """Retrieve all the menu items"""
        return Seller.objects.all().order_by("sellerBusinessName")


class LikePercentageChangeView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, sellerId, startDateTime, endDateTime, *args, **kwargs):
        # sellerId = self.request.query_params.get("sellerId")
        # startDateTime = self.request.query_params.get("startDateTime")
        # endDateTime = self.request.query_params.get("endDateTime")
        try:
            seller = Seller.objects.get(id=sellerId)
        except Seller.DoesNotExist:
            return Response({"error": "Seller not found"}, status=400)
        # Validate that the dates were provided
        if not startDateTime or not endDateTime:
            return Response({"error": "startDateTime and endDateTime query params are required"}, status=400)

        startDateTime = startDateTime.replace("_", " ").replace(
            "%20", " ").replace("%22", " ").replace("%3A", ":").strip('"').strip()
        endDateTime = endDateTime.replace("_", " ").replace("%20", " ").replace(
            "%22", " ").replace("%3A", ":").strip('"').strip()

        print('Start Date:', startDateTime)  # Debugging print statement
        print('End Date:', endDateTime)  # Debugging print statement

        # Parse the datetime strings into datetime objects
        try:
            startDateTime = datetime.strptime(
                startDateTime, "%Y-%m-%dT%H:%M:%S.%fZ")
            endDateTime = datetime.strptime(
                endDateTime, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            return Response({"error": "Invalid datetime format. Use ISO 8601 format 'YYYY-MM-DDTHH:MM:SS.sssZ'",
                             "startDate": startDateTime,
                             "sellerId": sellerId}, status=400,)

        # Get the seller's menu items
        menu_items = MenuItem.objects.filter(id__in=seller.menuItemId)

        # Get posts associated with seller's menu items
        posts = Post.objects.filter(menuItemId__in=menu_items)

        # Calcualte likes at startDateTime and endDateTie
        start_likes = posts.filter(postPublishDateTime__lte=startDateTime).aggregate(
            sum=Sum("postLikeCount"))["sum"] or 0
        end_likes = posts.filter(postPublishDateTime__lte=endDateTime).aggregate(
            sum=Sum("postLikeCount"))["sum"] or 0

        # calculate trend direction and percentage change
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

    def get(self, request, sellerId, startDateTime, endDateTime, *args, **kwargs):

        try:
            seller = Seller.objects.get(id=sellerId)
        except Seller.DoesNotExist:
            return Response({"error": "Seller not found"}, status=400)

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
                             "sellerId": sellerId}, status=400,)

        # Get the seller's menu items
        menu_items = MenuItem.objects.filter(id__in=seller.menuItemId)

        # Get posts associated with seller's menu items
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

        day = startDateTime
        while day <= endDateTime:
            # Get the cumulative sum of likes for posts up to and including this day
            likes = posts.filter(postPublishDateTime__lte=day).aggregate(
                sum=Sum("postLikeCount"))["sum"] or 0
            # Append the result to the results list
            results.append({"timestamp": day.isoformat(), "like": likes})
            # Move to the next step
            day += step

        # Return the result
        return Response({"totalPostLike": results})
