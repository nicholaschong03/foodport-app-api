from rest_framework import viewsets, status, permissions, authentication, generics, filters
from rest_framework.response import Response
from core.models import Dish
from dish.serializers import DishSerializer, DishDetailSerializer
from django.http import Http404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

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

class CustomDishPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class DishListView(generics.ListAPIView):
    """Return a list of dish filtered by dishName and seach query"""
    permissions_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]
    serializer_class = DishSerializer

    queryset = Dish.objects.all().order_by("dishName")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["sellerId"]
    search_fields = ["dishName"]
    pagination_class = CustomDishPagination

class RetrieveDishView(generics.RetrieveAPIView):
    """Retrieve a dish"""
    serializer_class = DishSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return a dish"""
        try:
            dish = Dish.objects.get(id=self.kwargs["id"])
        except Dish.DoesNotExist:
            raise Http404("Dish not found")
        return dish










