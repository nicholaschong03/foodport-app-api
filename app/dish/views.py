from rest_framework import viewsets, status, permissions, authentication
from rest_framework.response import Response
from core.models import Dish
from dish.serializers import DishSerializer, DishDetailSerializer

class DishViewset(viewsets.ModelViewSet):
    """Views for manage dish APIs"""
    serializer_class = DishDetailSerializer
    permissions_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]
    queryset = Dish.objects.all()

    def get_queryset(self):
        """Retrieve dishes for authenticated users"""
        user = self.request.user
        return self.queryset.filter(user=user).order_by("-id")

    def get_serializer_class(self):
        """Return serializer class for request"""
        if self.action == "list":
            return DishSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """create dishs """
        user = self.request.user
        serializer.save(user=user)






