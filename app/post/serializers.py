"""
Serializers for posts APIs
"""
from rest_framework import serializers

from core.models import Post, User, PostLike

class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post"""
    postPublishDateTime = serializers.SerializerMethodField()
    userId = serializers.ReadOnlyField(source="user.id")
    postId = serializers.ReadOnlyField(source="id")
    postPublishIpAddress = serializers.SerializerMethodField()
    postLikeCount = serializers.IntegerField(read_only=True)
    isLiked = serializers.SerializerMethodField()

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
            "menuItemId",
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
            "isLiked",
        ]
        read_only_fields = ["id", "userId", "postPublishDateTime", "isLiked"]

    def get_postPublishDateTime(self, obj):
        return obj.postPublishDateTime.isoformat()

    def get_postPublishIpAddress(self, obj):
        return obj.postPublishIpAddress

    def get_isLiked(self, obj):
        request = self.context.get("request", None)
        if request:
            user = request.user
            postLike = PostLike.objects.filter(post=obj, user=user).order_by("-likeDateTime").first()
            if postLike:
                return postLike.isActive
        return False

    def get_postLikeCount(self, obj):
        like_count = PostLike.objects.filter(post=obj, isActive=True).count()
        unlike_count = PostLike.objects.filter(post=obj, isActive=False).count()
        return like_count - unlike_count


class PostDetailSerializer(PostSerializer):
    """Serializer for post detail view"""

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields

class PostLikeSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    # post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    userId = serializers.SerializerMethodField(read_only=True)
    postId = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PostLike
        fields = [
            "id",
            "postId",
            "userId",
            "post",
            "user",
            "isActive",
            "likeDateTime",
            "likeIpAddress",
            "likeUserAgent",
        ]

    def get_userId(self, obj):
        return obj.user.id

    def get_postId(self, obj):
        return obj.post.id


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