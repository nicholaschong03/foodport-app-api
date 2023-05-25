"""
Views for the user API.
"""

from rest_framework import generics, authentication, permissions, views
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework import filters
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from user.serializer import UserSerializer, AuthTokenSerializer, UserProfileImageSerializer, UsersListSerializer, UserProfileCoverSerializer
from core.models import User
from rest_framework import status
from django.conf import settings

from ip2geotools.databases.noncommercial import DbIpCity

import os


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        """Handle HTTP POST request. """
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        response_data = {
            "idToken": token.key,
            "localId": user.id,
            "expiresIn": settings.EXPIRATION_TIME,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ManagerUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user"""
        user = self.request.user
        request = self.request
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        try:
            response = DbIpCity.get(ip, api_key="free")
            locatin = {
                "state": response.region,
                "country": response.country
            }
        except Exception as e:
            location = "Location unavailable"

        user.IPv4 = {
            "ipAddress": ip,
            "location": location
        }
        user.save()

        serializer_context = {"request": request, "ip_address": ip}
        serializer = self.serializer_class(user, context=serializer_context)
        return serializer.instance


class UploadProfileImageView(ManagerUserView):
    """Upload a profile image for the authenticated user"""
    serializer_class = UserProfileImageSerializer

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)

        if serializer.is_valid():
            if user.userProfilePictureUrl:
                old_profile_picture_path = os.path.join(
                    settings.MEDIA_ROOT, str(user.userProfilePictureUrl))
                if os.path.isfile(old_profile_picture_path):
                    os.remove(old_profile_picture_path)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UploadCoverPictureView(ManagerUserView):
    """Upload a cover image for the authenticated user"""
    serializer_class = UserProfileCoverSerializer

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)

        if serializer.is_valid():
            if user.userCoverPictureUrl:
                old_cover_picture_path = os.path.join(
                    settings.MEDIA_ROOT, str(user.userCoverPictureUrl)
                )
                if os.path.isfile(old_cover_picture_path):
                    os.remove(old_cover_picture_path)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class RetrieveUserView(generics.RetrieveAPIView):
    """Retrieve a user's profile"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve a return the requested user"""
        try:
            user = User.objects.get(id=self.kwargs["id"])
        except User.DoesNotExist:
            raise Http404("User not found")
        # serializer = self.serializer_class(user)
        # return serializer.data
        return user


class CustomUserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by("userName")
    serializer_class = UsersListSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["userName", "userUsername"]
    pagination_class = CustomUserPagination


class LogoutView(generics.GenericAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Remove the authentication token associated with the current user"""
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out"})


class FollowUserView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        try:
            user_to_follow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user == user_to_follow:
            return Response({"error": "User cannot follow themselves"}, status=status.HTTP_400_BAD_REQUEST)

        if user_to_follow in request.user.following.all():
            request.user.following.remove(user_to_follow)
            return Response({"status": "unfollowed"}, status=status.HTTP_200_OK)
        else:
            request.user.following.add(user_to_follow)
            return Response({"status": "followed"}, status=status.HTTP_200_OK)


class FollowersListView(generics.ListAPIView):
    serializer_class = UsersListSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404("User not found")
        return user.followers.all()


class FollowingListView(generics.ListAPIView):
    serializer_class = UsersListSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404("User not found")
        return user.following.all()


class FriendsListView(generics.ListAPIView):
    serializer_class = UsersListSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permissions_calsses = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404("User not found")
        return user.get_friends()
