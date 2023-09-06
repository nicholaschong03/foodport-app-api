from rest_framework import serializers

from core.models import Business, Post, MenuItem

from django.db.models import Avg, Min, Max

class BusinessSerializer(serializers.ModelSerializer):
    """Serializer for business"""
    post_photo_url = serializers.SerializerMethodField()
    businessId = serializers.ReadOnlyField(source="id")
    delicious_rating = serializers.SerializerMethodField()
    eat_again_rating = serializers.SerializerMethodField()
    worth_it_rating = serializers.SerializerMethodField()
    lowest_price = serializers.SerializerMethodField()
    highest_price = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = [
                  "businessId",
                  "businessName",
                  "post_photo_url",
                  "delicious_rating",
                  "eat_again_rating",
                  "worth_it_rating",
                  "lowest_price",
                  "highest_price",
                  "businessOperatingLocation",

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
        min_price = MenuItem.objects.filter(businessId=obj.id).aggregate(Min("price"))
        return min_price["price__min"]

    def get_highest_price(self, obj):
        max_price = MenuItem.objects.filter(businessId=obj.id).aggregate(Max("price"))
        return max_price["price__max"]



class BusinessDetailSerializer(BusinessSerializer):
    """Seriailzer for business detail view"""
    businessInfoContributor = serializers.SerializerMethodField()
    class Meta(BusinessSerializer.Meta):

        fields = BusinessSerializer.Meta.fields + [
                  "businessOperatingTime",
                  "businessVerified",
                  "businessSafeFood",
                  "businessHalal",
                  "businessInfoContributor",
                  "menuItemId",
                  "businessOwnerId",
        ]

    def get_businessInfoContributor(self,obj):
        return obj.businessInfoContributor

