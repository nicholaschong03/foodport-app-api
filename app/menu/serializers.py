from rest_framework import serializers

from core.models import MenuItem

from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation

from core.models import MenuItem, Post

from django.conf import settings
import os

class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for menu item """
    id = serializers.ReadOnlyField()
    post_photo_url = serializers.SerializerMethodField()
    class Meta:
        model = MenuItem
        fields = ["id",
                  "name",
                  "price",
                  "category",
                  "post_photo_url",
                  "sellerId",
                  ]

    def get_post_photo_url(self, obj):
       post = Post.objects.filter(menuItemId=obj.id).order_by("-postLikeCount").first()
       if post and post.postPhotoUrl:
           request = self.context.get("request")
           photo_url = post.postPhotoUrl.url
           return request.build_absolute_uri(photo_url)
       return None


class MenuItemDetailSerializer(MenuItemSerializer):
    """Detail serializer for Menu Item"""
    post_photos_url = serializers.SerializerMethodField()
    class Meta(MenuItemSerializer.Meta):
        fields = MenuItemSerializer.Meta.fields + [
                  "basicIngredient",
                  "compositeIngredient",
                  "nutritionFacts",
                  "postId",
                  "dishInfoContributor",
                  "totalPostCount",
                  "deliciousRating",
                  "eatAgainRating",
                  "worthItRating",
                  "trendingPosition",
                  "trendingDirection",
                  "post_photos_url"]

    def get_post_photos_url(self, obj):
        request = self.context.get("request")
        posts = Post.objects.filter(menuItemId=obj.id).order_by("-postLikeCount")
        return {post.id: request.build_absolute_uri(post.postPhotoUrl.url) for post in posts if post.postPhotoUrl}


