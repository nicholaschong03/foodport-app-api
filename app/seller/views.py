from rest_framework import viewsets, status, permissions, authentication
from rest_framework.response import Response
from core.models import Seller
from seller.serializers import SellerSerializer, SellerDetailSerializer

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
        serializer.save(user=user)




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


