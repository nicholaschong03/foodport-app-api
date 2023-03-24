from rest_framework import serializers

from core.models import Seller

class SellerSerializer(serializers.ModelSerializer):
    """Serializer for seller"""
    sellerId = serializers.ReadOnlyField(source="id")
    class Meta:
        model = Seller
        fields = ["sellerName",
                  "sellerId",
                  "sellerOperatingLocation",
                  "sellerOperatingTime",
                  "sellerVerified",
                  "sellerSafeFood",
                  "sellerHalal",]

class SellerDetailSerializer(SellerSerializer):
    """Seriailzer for seller detail view"""

    class Meta(SellerSerializer.Meta):
        fields = SellerSerializer.Meta.fields


