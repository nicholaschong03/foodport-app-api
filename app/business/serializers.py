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
    businessTotalPostCount = serializers.SerializerMethodField()
    businessFollowerCount = serializers.SerializerMethodField()
    businessFollowerId = serializers.SerializerMethodField()
    postId = serializers.SerializerMethodField()

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
                  "businessOperatingLatitude",
                  "businessOperatingLongitude",
                  "businessTotalPostCount",
                  "businessFollowerCount",
                  "businessFollowerId",
                  "postId",
                  ]



    def get_post_photo_url(self, obj):
        menu_items = obj.menu_items.all()
        posts = [menu_item.posts.order_by("-postLikeCount").first() for menu_item in menu_items]
        posts = [post for post in posts if post]

        post = None
        if posts:
            post = max(posts, key=lambda post: post.postLikeCount)

        if post and post.postPhotoUrl:
            request = self.context.get("request")
            photo_url = post.postPhotoUrl.url
            return request.build_absolute_uri(photo_url)
        return None

    def get_delicious_rating(self, obj):
        menu_items = obj.menu_items.all()
        ratings = []
        for menu_item in menu_items:
            avg_rating = menu_item.posts.aggregate(Avg("postRatingDelicious"))
            if avg_rating["postRatingDelicious__avg"] is not None:
                ratings.append(avg_rating["postRatingDelicious__avg"])
        if ratings:
            return sum(ratings) / len(ratings)
        return None

    def get_eat_again_rating(self, obj):
        menu_items = obj.menu_items.all()
        ratings = []
        for menu_item in menu_items:
            avg_rating = menu_item.posts.aggregate(Avg("postRatingEatAgain"))
            if avg_rating["postRatingEatAgain__avg"] is not None:
                ratings.append(avg_rating["postRatingEatAgain__avg"])
        if ratings:
            return sum(ratings) / len(ratings)
        return None

    def get_worth_it_rating(self, obj):
        menu_items = obj.menu_items.all()
        ratings = []
        for menu_item in menu_items:
            avg_rating = menu_item.posts.aggregate(Avg("postRatingWorthIt"))
            if avg_rating["postRatingWorthIt__avg"] is not None:
                ratings.append(avg_rating["postRatingWorthIt__avg"])
        if ratings:
            return sum(ratings) / len(ratings)
        return None

    def get_lowest_price(self, obj):
        min_price = obj.menu_items.aggregate(Min("price"))
        return min_price["price__min"]

    def get_highest_price(self, obj):
        max_price = obj.menu_items.aggregate(Max("price"))
        return max_price["price__max"]

    def get_businessTotalPostCount(self, obj):
        menu_items = obj.menu_items.all()
        total_post_count = sum(menu_item.posts.count() for menu_item in menu_items)
        return total_post_count


    def get_businessFollowerCount(self, obj):
        return obj.followers.count()

    def get_businessFollowerId(self, obj):
        return [follower.id for follower in obj.followers.all()]

    def get_postId(self, obj):
        post_ids = []
        menu_items = obj.menu_items.all()
        for menu_item in menu_items:
            post_ids.extend(menu_item.posts.values_list("id", flat=True))

        return post_ids




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
                  "sellerId",
        ]

    def get_businessInfoContributor(self,obj):
        return obj.businessInfoContributor

