"""
Views for the user API.
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from django.http import Http404
from user.serializer import UserSerializer, AuthTokenSerializer, UserProfileImageSerializer
from core.models import User
from rest_framework import status
from django.conf import settings



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

class LogoutView(generics.GenericAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Remove the authentication token associated with the current user"""
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out"})
