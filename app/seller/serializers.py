from rest_framework import serializers

from core.models import Seller, Post, MenuItem

from django.db.models import Avg, Min, Max

class SellerSerializer(serializers.ModelSerializer):
    """Serializer for seller"""
    post_photo_url = serializers.SerializerMethodField()
    sellerId = serializers.ReadOnlyField(source="id")
    delicious_rating = serializers.SerializerMethodField()
    eat_again_rating = serializers.SerializerMethodField()
    worth_it_rating = serializers.SerializerMethodField()
    lowest_price = serializers.SerializerMethodField()
    highest_price = serializers.SerializerMethodField()

    class Meta:
        model = Seller
        fields = [
                  "sellerId",
                  "sellerBusinessName",
                  "post_photo_url",
                  "delicious_rating",
                  "eat_again_rating",
                  "worth_it_rating",
                  "lowest_price",
                  "highest_price",
                  "sellerOperatingLocation",

                  ]



    def get_post_photo_url(self, obj):
       for menuId in obj.menuItemId:
           post = Post.objects.filter(menuItemId=menuId).order_by("-postLikeCount").first()
           if post and post.postPhotoUrl:
                request = self.context.get("request")
                photo_url = post.postPhotoUrl.url
                return request.build_absolute_uri(photo_url)
       return None

    def get_delicious_rating(self, obj):
        ratings = []
        for menuId in obj.menuItemId:
            avg_rating = Post.objects.filter(menuItemId=menuId).aggregate(Avg("postRatingDelicious"))
            if avg_rating["postRatingDelicious__avg"] is not None:
                ratings.append(avg_rating["postRatingDelicious__avg"])
        if ratings:
            return sum(ratings) / len(ratings)
        return None

    def get_eat_again_rating(self, obj):
        ratings = []
        for menuId in obj.menuItemId:
            avg_rating = Post.objects.filter(menuItemId=menuId).aggregate(Avg("postRatingEatAgain"))
            if avg_rating["postRatingEatAgain__avg"] is not None:
                ratings.append(avg_rating["postRatingEatAgain__avg"])
        if ratings:
            return sum(ratings) / len(ratings)
        return None

    def get_worth_it_rating(self, obj):
        ratings = []
        for menuId in obj.menuItemId:
            avg_rating = Post.objects.filter(menuItemId=menuId).aggregate(Avg("postRatingWorthIt"))
            if avg_rating["postRatingWorthIt__avg"] is not None:
                ratings.append(avg_rating["postRatingWorthIt__avg"])
        if ratings:
            return sum(ratings) / len(ratings)
        return None

    def get_lowest_price(self, obj):
        min_price = MenuItem.objects.filter(sellerId=obj.id).aggregate(Min("price"))
        return min_price["price__min"]

    def get_highest_price(self, obj):
        max_price = MenuItem.objects.filter(sellerId=obj.id).aggregate(Max("price"))
        return max_price["price__max"]



class SellerDetailSerializer(SellerSerializer):
    """Seriailzer for seller detail view"""
    sellerInfoContributor = serializers.SerializerMethodField()
    class Meta(SellerSerializer.Meta):

        fields = SellerSerializer.Meta.fields + [
                  "sellerOperatingTime",
                  "sellerVerified",
                  "sellerSafeFood",
                  "sellerHalal",
                  "sellerInfoContributor",
                  "menuItemId",
                  "sellerOwnerId",
        ]

    def get_sellerInfoContributor(self,obj):
        return obj.sellerInfoContributor

