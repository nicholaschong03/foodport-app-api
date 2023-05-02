from rest_framework import serializers

from core.models import Seller

class SellerSerializer(serializers.ModelSerializer):
    """Serializer for seller"""
    sellerId = serializers.ReadOnlyField(source="id")
    sellerInfoContributor = serializers.SerializerMethodField()
    class Meta:
        model = Seller
        fields = [
                  "sellerId",
                  "sellerBusinessName",
                  "sellerOperatingLocation",
                  "sellerOperatingTime",
                  "sellerVerified",
                  "sellerSafeFood",
                  "sellerHalal",
                  "sellerInfoContributor",
                  "dishId",
                  "sellerOwnerId",]

    def get_sellerInfoContributor(self,obj):
        return obj.sellerInfoContributor


class SellerDetailSerializer(SellerSerializer):
    """Seriailzer for seller detail view"""

    class Meta(SellerSerializer.Meta):
        fields = SellerSerializer.Meta.fields


