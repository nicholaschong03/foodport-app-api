from rest_framework import viewsets, status, permissions, authentication, generics, filters
from rest_framework.response import Response
from core.models import MenuItem
from menu.serializers import MenuItemSerializer, MenuItemDetailSerializer
from django.http import Http404

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

class MenuItemViewset(viewsets.ModelViewSet):
    """Views for manage menu item APIs"""
    serializer_class = MenuItemDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = MenuItem.objects.all()

    def get_queryset(self):
        """Retrieve menu items for authenticated users"""
        user = self.request.user
        return self.queryset.filter(user=user).order_by("-id")

    def get_serializer_class(self):
        """Return serializer class for request"""
        if self.action == "list":
            return MenuItemSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """create menu items """
        user = self.request.user
        serializer.save(user=user)

class CustomMenuItemPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class MenuItemListView(generics.ListAPIView):
    """Return a list of menu filtered by menu item Name and seach query"""
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]
    serializer_class = MenuItemSerializer

    queryset = MenuItem.objects.all().order_by("name")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "businessId"]
    search_fields = ["name"]
    pagination_class = CustomMenuItemPagination

class RetrieveMenuItemView(generics.RetrieveAPIView):
    """Retrieve a menu item"""
    serializer_class = MenuItemDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Retrieve and return a menu item"""
        try:
            menuItem = MenuItem.objects.get(id=self.kwargs["id"])
        except MenuItem.DoesNotExist:
            raise Http404("Menu item not found")
        return menuItem

class AllMenuItemListView(generics.ListAPIView):
    """Return a list of all existing menu items"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        """Retrieve all the menu items"""
        return MenuItem.objects.all().order_by("name")


# class CategoryMenuItemListView(generics.ListAPIView):
#     """Return a list of all existing menu items based on category"""
#     permission_classes = [permissions.IsAuthenticated]
#     authentication_classes = [authentication.TokenAuthentication]
#     serializer_class = MenuItemSerializer

#     queryset = MenuItem.objects.all().order_by("name")
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     filterset_fields = ["category", "sellerId"]
#     search_fields = ["name"]
#     pagination_class = CustomMenuItemPagination












