from rest_framework import viewsets, status, permissions, authentication, generics
from rest_framework.response import Response
from core.models import Seller
from seller.serializers import SellerSerializer, SellerDetailSerializer
from django.utils import timezone
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

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
        serializer.save(user=user, sellerInfoContributor=seller_info_contributor)


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
    serializer_class = SellerSerializer
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




#     def create(self, request, *args, **kwargs):
#         user = request.user
#         serializer = self.get_serializer(data=request.data)
#         serializer.save(user=user)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# class SellerRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
#     serializer_class = SellerSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     authentication_classes = [authentication.TokenAuthentication]
#     queryset = Seller.objects.all()

#     def get_queryset(self):
#         user = self.request.user
#         return self.queryset.filter(user=user).order_by("id")

# class SellerDeleteAPIView(generics.DestroyAPIView):
#     serializer_class = SellerSerializer
#     queryset = Seller.objects.all()
#     permission_classes = [permissions.IsAuthenticated]
#     authentication_classes = [authentication.TokenAuthentication]

#     def perform_destroy(self, instance):
#         user = self.request.user
#         if instance.user == user:
#            instance.delete()
#         else:
#             return Response({"detail": "Seller profile not found"},
#                             status = status.HTTP_404_BAD_REQUEST)


