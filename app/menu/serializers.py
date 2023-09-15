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
                  ]

    def get_post_photo_url(self, obj):
       post = Post.objects.filter(menuItemId=obj.id).order_by("-postLikeCount").first()
       if post and post.postPhotoUrl:
           request = self.context.get("request")
           photo_url = post.postPhotoUrl.url
           return request.build_absolute_uri(photo_url)
       return None

    def get_delicious_rating(self, obj):
        avg_rating = Post.objects.filter(menuItemId=obj.id).aggregate(Avg('postRatingDelicious'))
        return avg_rating["postRatingDelicious__avg"]

    def get_eat_again_rating(self, obj):
        avg_rating = Post.objects.filter(menuItemId=obj.id).aggregate(Avg('postRatingDelicious'))
        return avg_rating["postRatingDelicious__avg"]

    def get_worth_it_rating(self, obj):
        avg_rating = Post.objects.filter(menuItemId=obj.id).aggregate(Avg('postRatingDelicious'))
        return avg_rating["postRatingDelicious__avg"]

    def get_menuItemTotalPostCount(self, obj):
        if obj.postId:
            return len(obj.postId)
        return 0



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
                  "trendingPosition",
                  "trendingDirection",
                  "post_photos_url"]

    def get_post_photos_url(self, obj):
        request = self.context.get("request")
        posts = Post.objects.filter(menuItemId=obj.id).order_by("-postLikeCount")
        return {post.id: request.build_absolute_uri(post.postPhotoUrl.url) for post in posts if post.postPhotoUrl}


