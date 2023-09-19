"""
Serializers for posts APIs
"""
from rest_framework import serializers

from core.models import Post, User, PostLike, PostSave, PostView, PostComment, Business, PostShare, MenuItem, CommentLike


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post"""
    postPublishDateTime = serializers.SerializerMethodField()
    userId = serializers.ReadOnlyField(source="user.id")
    postId = serializers.ReadOnlyField(source="id")
    postPublishIpAddress = serializers.SerializerMethodField()
    postLikeCount = serializers.SerializerMethodField()
    isLiked = serializers.SerializerMethodField()
    userProfilePictureUrl = serializers.SerializerMethodField()
    businessOperatingLocation = serializers.SerializerMethodField()
    userUsername = serializers.ReadOnlyField(source="user.userUsername")
    menuItemName = serializers.SerializerMethodField()
    menuItemBasicIngredient = serializers.SerializerMethodField()
    menuItemCompositeIngredient = serializers.SerializerMethodField()
    menuItemNutritionFacts = serializers.SerializerMethodField()
    businessId = serializers.SerializerMethodField()
    postCommentCount = serializers.SerializerMethodField()
    postSaveCount = serializers.SerializerMethodField()
    postShareCount = serializers.SerializerMethodField()
    isSaved = serializers.SerializerMethodField()

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
            "businessOperatingLocation",
            "userUsername",
            "menuItemName",
            "menuItemBasicIngredient",
            "menuItemCompositeIngredient",
            "menuItemNutritionFacts",
            "businessId",
            "postCommentCount",
            "postSaveCount",
            "postShareCount",
            "isSaved",
            "menuItem",

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
            postLike = PostLike.objects.filter(
                post=obj, user=user).order_by("-likeDateTime").first()
            if postLike:
                return postLike.isActive
        return False

    def get_postLikeCount(self, obj):
        like_count = PostLike.objects.filter(post=obj, isActive=True).count()
        unlike_count = PostLike.objects.filter(
            post=obj, isActive=False).count()
        return like_count - unlike_count

    def get_userProfilePictureUrl(self, obj):
        user = obj.user
        if user and user.userProfilePictureUrl:
            request = self.context.get("request")
            photo_url = user.userProfilePictureUrl.url
            return request.build_absolute_uri(photo_url)
        return None

    def get_businessOperatingLocation(self, obj):
        try:
            business_instance = obj.menuItem.business
            if business_instance:
                return business_instance.businessOperatingLocation
        except AttributeError:
            return None

    def get_menuItemName(self, obj):
        try:
            menu_item = obj.menuItem
            return menu_item.name
        except AttributeError:
            return None

    def get_menuItemBasicIngredient(self, obj):
        try:
            menu_item = obj.menuItem
            return menu_item.basicIngredient
        except AttributeError:
            return None

    def get_menuItemCompositeIngredient(self, obj):
        try:
            menu_item = obj.menuItem
            return menu_item.compositeIngredient
        except AttributeError:
            return None

    def get_menuItemNutritionFacts(self, obj):
        try:
            menu_item = obj.menuItem
            return menu_item.nutritionFacts
        except AttributeError:
            return None

    def get_businessId(self, obj):
        try:
            menu_item = obj.menuItem
            return menu_item.business.id
        except AttributeError:
            return None

    def get_postCommentCount(self, obj):
        return PostComment.objects.filter(post=obj).count()

    def get_postSaveCount(self, obj):
        return PostSave.objects.filter(post=obj).count()

    def get_postShareCount(self, obj):
        return PostShare.objects.filter(post=obj).count()

    def get_isSaved(self, obj):
        request = self.context.get("request", None)
        if request:
            user = request.user
            postSave = PostSave.objects.filter(
                post=obj, user=user).order_by("-savedDateTime").first()
            if postSave:
                return postSave.postIsSaved
        return False

class PostDistanceSerializer(PostSerializer):
    """Serializer for nearbyPostListView"""
    distance = serializers.SerializerMethodField()

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ["distance"]

    def get_distance(self, obj):
        try:
            return obj.distance
        except AttributeError:
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

class CommentLikeSerializer(serializers.ModelSerializer):
    userId = serializers.SerializerMethodField(read_only=True)
    commentId = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CommentLike
        fields = [
            "id",
            "commentId",
            "userId",
            "comment",
            "user",
            "isActive",
            "likeDateTime",
            "likeIpAddress",
            "likeUserAgent",
        ]

    def get_userId(self, obj):
        return obj.user.id

    def get_commentId(self, obj):
        return obj.comment.id


class PostSaveSerializer(serializers.ModelSerializer):
    userId = serializers.ReadOnlyField(source="user.id")
    postId = serializers.ReadOnlyField(source="post.id")

    class Meta:
        model = PostSave
        fields = ["id", "userId", "postId", "postIsSaved",
                  "savedDateTime", "unsavedDateTime"]
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
    postCommentId = serializers.ReadOnlyField(source="id")
    userName = serializers.SerializerMethodField(read_only=True)
    userPhotoUrl = serializers.SerializerMethodField(read_only=True)
    isLiked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PostComment
        fields = [
            "postCommentId",
            "postId",
            "userId",
            "commentContent",
            "commentPublishDateTime",
            "commentPublishIpAddress",
            "commentUserAgent",
            "commentLikes",
            "commentReplies",
            "commentPublishLocation",
            "userName",
            "commentPublishLastUpdatedDateTime",
            "userPhotoUrl",
            "isLiked",
            "commentLikeCount",

        ]

    def get_userName(self, obj):
        username = obj.user.userName
        if username:
            return username
        return None

    def get_userPhotoUrl(self, obj):
        user = obj.user
        if user and user.userProfilePictureUrl:
            request = self.context.get("request")
            photo_url = user.userProfilePictureUrl.url
            return request.build_absolute_uri(photo_url)
        return None

    def get_isLiked(self, obj):
        request = self.context.get("request", None)
        if request:
            user = request.user
            commentLike = CommentLike.objects.filter(
                comment=obj, user=user).order_by("-likeDateTime").first()
            if commentLike:
                return commentLike.isActive
        return False



class PostShareSerializer(serializers.ModelSerializer):
    sharedById = serializers.SerializerMethodField(read_only=True)
    sharedToId = serializers.SerializerMethodField(read_only=True)
    postId = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PostShare
        fields = [
            "id",
            "postId",
            "sharedById",
            "sharedToId",
            "sharedDateTime",
            "sharedBy",
            "sharedTo",
            "post"

        ]

    def get_sharedById(self, obj):
        return obj.sharedBy.id

    def get_sharedToId(self, obj):
        return obj.sharedTo.id

    def get_postId(self, obj):
        return obj.post.id


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

    def get_userProfilePictureUrl(self, obj):
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
        fields = ["userId", "userUsername",
                  "userName", "userProfilePictureUrl"]


