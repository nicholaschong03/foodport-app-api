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
from django.http import Http404, JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from user.serializer import UserSerializer, AuthTokenSerializer, UserProfileImageSerializer, UsersListSerializer, UserProfileCoverSerializer
from core.models import User
from rest_framework import status
from django.conf import settings

from rest_framework.views import APIView

from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import sys

from ip2geotools.databases.noncommercial import DbIpCity

import os

from firebase_admin import auth

from PIL import Image
from io import BytesIO


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


# class GoogleAuthView(APIView):

#     def post(self, request):
#         strategy = load_strategy(request)
#         backend = load_backend(strategy=strategy, name='google-oauth2', redirect_uri=None)


#         try:

#             if isinstance(backend, BaseOAuth2):
#                 # Check if user is authenticated
#                 access_token = request.data.get("access_token")
#                 if not access_token:
#                     return Response({"error": "Missing access token"}, status=status.HTTP_400_BAD_REQUEST)

#                 if not request.user.is_authenticated:
#                     # Generate the social token
#                     social = backend.do_auth(access_token=access_token)
#                 else:
#                     social = backend.do_auth(access_token=access_token, user=request.user)

#                 if social and social.user:
#                     social.user.set_unusable_password()
#                     social.user.save()
#                     token, _ = Token.objects.get_or_create(user=social.user)

#                     return Response({
#                         "token": token.key,
#                         "localId": social.user.id,
#                         "expiresIn": settings.EXPIRATION_TIME
#                     }, status=status.HTTP_200_OK)

#             else:
#                 return Response({
#                     "error": "Wrong backend type"
#                 }, status=status.HTTP_400_BAD_REQUEST)

#         except MissingBackend:
#             return Response({
#                 "error": "Backend not found"
#             }, status=status.HTTP_400_BAD_REQUEST)


class FirebaseAuthView(APIView):
    """Log in or register a user using a Firebase token."""

    def post(self, request):
        id_token = request.data.get("idToken")
        local_id = request.data.get("localId")
        if local_id:
            # If localId is provided, the user is already logged in before, try to find them and return the token
            try:
                user = User.objects.get(id=local_id)
                token = Token.objects.get(user=user)
                response_data = {
                    "idToken": token.key,
                    "localId": user.id,
                    "expiresIn": settings.EXPIRATION_TIME,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
            except Token.DoesNotExist:
                return Response({"error": "Token does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # If localId is not provided, verify the id_token with Firebase
            if not id_token:
                return Response({"error": "Missing ID token"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                decoded_token = auth.verify_id_token(id_token)
                firebase_uid = decoded_token["uid"]
            except ValueError as exc:
                return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(firebase_uid=firebase_uid)
            except User.DoesNotExist:
                user_email = decoded_token.get("email")
                name = decoded_token.get("name")
                username = decoded_token.get("username")
                profile_picture = decoded_token.get("picture")

                user = User.objects.create_user(
                    userEmailAddress=user_email, firebase_uid=firebase_uid, userName=name, userUserName=username, userProfilePictureUrl=profile_picture)
                user.save()

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
            location = {
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

    def compress_image(self, image):
        image_temporary = Image.open(image)
        output_io_stream = BytesIO()
        image_temporary.save(output_io_stream , format='JPEG', quality=60)
        output_io_stream.seek(0)
        image = ContentFile(output_io_stream.read(), f"{image.name.split('.')[0]}.jpeg")
        return image

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        data = request.data.copy()  # make a copy of the data
        data['userProfilePictureUrl'] = self.compress_image(request.FILES['userProfilePictureUrl'])  # compress image and assign it back
        serializer = self.get_serializer(user, data=data)

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

    def compress_image(self, image):
        image_temporary = Image.open(image)
        output_io_stream = BytesIO()
        image_temporary.save(output_io_stream , format='JPEG', quality=60)
        output_io_stream.seek(0)
        image = ContentFile(output_io_stream.read(), f"{image.name.split('.')[0]}.jpeg")
        return image

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        data = request.data.copy()  # make a copy of the data
        data['userCoverPictureUrl'] = self.compress_image(request.FILES['userCoverPictureUrl'])  # compress image and assign it back
        serializer = self.get_serializer(user, data=data)

        if serializer.is_valid():
            if user.userCoverPictureUrl:
                old_cover_picture_path = os.path.join(
                    settings.MEDIA_ROOT, str(user.userCoverPictureUrl)
                )
                if os.path.isfile(old_cover_picture_path):
                    os.remove(old_cover_picture_path)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
