from rest_framework import serializers

from core.models import MenuItem

from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation

from core.models import MenuItem, Post

from django.db.models import Avg

from django.conf import settings

class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for menu item """
    id = serializers.ReadOnlyField()
    post_photo_url = serializers.SerializerMethodField()
    delicious_rating = serializers.SerializerMethodField()
    eat_again_rating = serializers.SerializerMethodField()
    worth_it_rating = serializers.SerializerMethodField()
    menuItemTotalPostCount = serializers.SerializerMethodField()
    businessId = serializers.SerializerMethodField()
    class Meta:
        model = MenuItem
        fields = ["id",
                  "name",
                  "price",
                  "category",
                  "post_photo_url",
                  "businessId",
                  "delicious_rating",
                  "eat_again_rating",
                  "worth_it_rating",
                  "menuItemTotalPostCount",
                  "business"
                  ]

    def get_post_photo_url(self, obj):
       post = obj.posts.order_by("-postLikeCount").first()
       if post and post.postPhotoUrl:
           request = self.context.get("request")
           photo_url = post.postPhotoUrl.url
           return request.build_absolute_uri(photo_url)
       return None

    def get_delicious_rating(self, obj):
        avg_rating = obj.posts.aggregate(Avg('postRatingDelicious'))
        return avg_rating["postRatingDelicious__avg"]

    def get_eat_again_rating(self, obj):
        avg_rating = obj.posts.aggregate(Avg('postRatingDelicious'))
        return avg_rating["postRatingDelicious__avg"]

    def get_worth_it_rating(self, obj):
        avg_rating = obj.posts.aggregate(Avg('postRatingDelicious'))
        return avg_rating["postRatingDelicious__avg"]

    def get_menuItemTotalPostCount(self, obj):
        total_post_count = obj.posts.count()
        return total_post_count

    def get_businessId(self, obj):
        if obj.business:
            return obj.business.id
        else:
            return None




class MenuItemDetailSerializer(MenuItemSerializer):
    """Detail serializer for Menu Item"""
    post_photos_url = serializers.SerializerMethodField()
    class Meta(MenuItemSerializer.Meta):
        fields = MenuItemSerializer.Meta.fields + [
                  "basicIngredient",
                  "compositeIngredient",
                  "nutritionFacts",
                  "dishInfoContributor",
                  "trendingPosition",
                  "trendingDirection",
                  "post_photos_url"]

    def get_post_photos_url(self, obj):
        request = self.context.get("request")
        posts = obj.posts.order_by("-postLikeCount")
        return {post.id: request.build_absolute_uri(post.postPhotoUrl.url) for post in posts if post.postPhotoUrl}


