"""
Views for the user API.
"""

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from user.serializer import UserSerializer, AuthTokenSerializer
from rest_framework import status
from django.conf import settings

from datetime import datetime, timedelta
import pytz

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
        return self.request.user

class LogoutView(generics.GenericAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Remove the authentication tokena associated with the current user"""
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out"})