from rest_framework import serializers

from core.models import Dish

class DishSerializer(serializers.ModelSerializer):
    """Serializer for dish"""
    dishId = serializers.ReadOnlyField(source="id")
    class Meta:
        model = Dish
        fields = ["dishId",
                  "dishName",
                  "dishPrice",
                  "dishIngredient",
                  "dishMainIngredient",
                  "dishNutrition",
                  "sellerId",
                  "postId",
                  "dishInfoContributor",]

class DishDetailSerializer(DishSerializer):
    """Detail serializer for Dish"""
    class Meta(DishSerializer.Meta):
        fields = DishSerializer.Meta.fields