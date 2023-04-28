"""
Serializers for posts APIs
"""
from rest_framework import serializers

from core.models import Post, User

class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post"""
    postPublishDateTime = serializers.SerializerMethodField()
    userId = serializers.ReadOnlyField(source="user.id")
    postId = serializers.ReadOnlyField(source="id")
    postPublishIpAddress = serializers.SerializerMethodField()
    postLikeCount = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "postId",
            "userId",
            "postReview",
            "postPublishDateTime",
            "postRatingDelicious",
            "postRatingEatAgain",
            "postRatingWorthIt",
            "postPhotoUrl",
            "dishId",
            "postPublishIpAddress",
            "postView",
            "postLikeCount",
            "postComment",
            "postCommentView",
            "postSave",
            "postDishSellerVisit",
            "postDishVisit",
            "postView",
            "postShare",
        ]
        read_only_fields = ["id", "userId", "postPublishDateTime"]

    def get_postPublishDateTime(self, obj):
        return obj.postPublishDateTime.isoformat()

    def get_postPublishIpAddress(self, obj):
        return obj.postPublishIpAddress

    def get_postLikeCount(self, obj):
        return obj.postLike.count()


class PostDetailSerializer(PostSerializer):
    """Serializer for post detail view"""

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields

class PostImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to reipes"""

    class Meta:
        model = Post
        fields = ["id", "postPhotoUrl"]
        read_only_fields = ["id"]
        extra_kwargs = {"postPhotoUrl": {"required": "True"}}


class UsersListSerializer(serializers.ModelSerializer):
    """Serializer for retrieving a list of users"""
    userId = serializers.ReadOnlyField(source="id")
    class Meta:
        model = User
        fields = ["userId", "userUsername", "userName", "userProfilePictureUrl"]