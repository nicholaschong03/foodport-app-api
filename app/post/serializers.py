"""
Serializers for posts APIs
"""
from rest_framework import serializers

from core.models import Post, User, PostLike, PostSave, PostView, PostComment, Seller

class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post"""
    postPublishDateTime = serializers.SerializerMethodField()
    userId = serializers.ReadOnlyField(source="user.id")
    postId = serializers.ReadOnlyField(source="id")
    postPublishIpAddress = serializers.SerializerMethodField()
    postLikeCount = serializers.SerializerMethodField()
    isLiked = serializers.SerializerMethodField()
    userProfilePictureUrl = serializers.SerializerMethodField()
    sellerOperatingLocation = serializers.SerializerMethodField()
    userUsername = serializers.ReadOnlyField(source="user.userUsername")




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
            "userProfilePictureUrl",
            "sellerOperatingLocation",
            "userUsername",

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

    def get_userProfilePictureUrl(self, obj):
        user = obj.user
        if user and user.userProfilePictureUrl:
            request = self.context.get("request")
            photo_url = user.userProfilePictureUrl.url
            return request.build_absolute_uri(photo_url)
        return None


    def get_sellerOperatingLocation(self, obj):
        menu_id = obj.menuItemId
        seller_instance = Seller.objects.filter(menuItemId=menu_id)

        if seller_instance:
            return seller_instance.sellerOperatingLocation
        return None




class PostDetailSerializer(PostSerializer):
    """Serializer for post detail view"""

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields

class PostLikeSerializer(serializers.ModelSerializer):
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

class PostSaveSerializer(serializers.ModelSerializer):
    userId = serializers.ReadOnlyField(source="user.id")
    postId = serializers.ReadOnlyField(source="post.id")

    class Meta:
        model = PostSave
        fields = ["id", "userId", "postId", "postIsSaved", "savedDateTime", "unsavedDateTime"]
        read_only_fields = ["id", "savedDateTime", "unsavedDateTime"]

class PostViewSerializer(serializers.ModelSerializer):
    userId = serializers.SerializerMethodField(read_only=True)
    postId = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PostView
        fields = [
            "id",
            "postId",
            "userId",
            "post",
            "user",
            "viewDateTime",
            "viewUserAgent"
        ]

    def get_userId(self, obj):
        return obj.user.id

    def get_postId(self, obj):
        return obj.post.id


class PostCommentSerializer(serializers.ModelSerializer):
    userId = serializers.ReadOnlyField(source="user.id")
    postId = serializers.ReadOnlyField(source="post.id")

    class Meta:
        model = PostComment
        fields = [
            "id",
            "postId",
            "userId",
            "comment",
            "commentDateTime",
            "commentIpAddress",
            "commentUserAgent"
        ]



class PostReviewRatingSerializer(serializers.ModelSerializer):
    """Serializer for filtering Post objects by menuItemId"""
    postId = serializers.ReadOnlyField(source="id")
    userId = serializers.ReadOnlyField(source="user.id")
    userProfilePictureUrl = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "postId",
            "postReview",
            "postRatingEatAgain",
            "postRatingWorthIt",
            "postRatingDelicious",
            "userId",
            "userProfilePictureUrl",
        ]

    def get_userProfilePictureUrl(self,obj):
        if obj.user.userProfilePictureUrl and hasattr(obj.user.userProfilePictureUrl, 'url'):
            return obj.user.userProfilePictureUrl.url
        else:
            return None


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