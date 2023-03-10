"""
Serializers for posts APIs
"""
from rest_framework import serializers

from core.models import Post

class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post"""
    postPublishDateTime = serializers.SerializerMethodField()
    userId = serializers.ReadOnlyField(source="user.id")
    postId = serializers.ReadOnlyField(source="id")

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
            "postLike",
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