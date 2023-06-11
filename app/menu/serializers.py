from rest_framework import serializers

from core.models import MenuItem

from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation

import decimal

class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for menu item """
    id = serializers.ReadOnlyField()
    class Meta:
        model = MenuItem
        fields = ["id",
                  "name",
                  "price",
                  "basicIngredient",
                  "category",
                  "compositeIngredient",
                  "nutritionFacts",
                  "sellerId",
                  "postId",
                  "dishInfoContributor",
                  "totalPostCount",
                  "deliciousRating",
                  "eatAgainRating",
                  "worthItRating",
                  "trendingPosition",
                  "trendingDirection",
                  ]


class MenuItemDetailSerializer(MenuItemSerializer):
    """Detail serializer for Menu Item"""
    class Meta(MenuItemSerializer.Meta):
        fields = MenuItemSerializer.Meta.fields

