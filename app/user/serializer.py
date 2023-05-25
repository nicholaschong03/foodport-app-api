"""
Serializer for the user API View.
"""

from django.contrib.auth import (
    get_user_model,
    authenticate
)

from django.utils.translation import gettext as _

from rest_framework import serializers

from django.utils.translation import gettext as _

from core.models import Post, User




class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    userPostId = serializers.SerializerMethodField()
    userId = serializers.ReadOnlyField(source="id")
    userFollowerCount = serializers.SerializerMethodField()
    userFollowingCount = serializers.SerializerMethodField()
    userFriendCount = serializers.SerializerMethodField()
    userFollowerId = serializers.SerializerMethodField()
    userFollowingId = serializers.SerializerMethodField()
    userLikeCount = serializers.SerializerMethodField()


    class Meta:
        model = get_user_model()
        fields = ["userEmailAddress",
                  "password",
                  "userUsername",
                  "userName",
                  "userPhoneNumber",
                  "userId",
                  "userBio",
                  "userGender",
                  "userShowBirthDate",
                  "userProfilePictureUrl",
                  "userCoverPictureUrl",
                  "userFollowerCount",
                  "userFollowingCount",
                  "userFollowerId",
                  "userFollowingId",
                  "userFriendCount",
                  "userLikeCount",
                  "userBirthDate",
                  "userLocation",
                  "userAccountRegisterDate",
                  "IPv4",
                  "userPostId",
                  "userPostLike",
                  "userPostComment",
                  "userPostSave",
                  "userPostShare",
                  "userPostView",
                  "userPostCommentView",
                  "userPostDishVisit",
                  "userPostDishSellerVisit",
                    ]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5},
                        "userUsername": {"required": False}}

    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def get_userPostId(self,obj):
        """Method to get the list of postId related to the user"""
        posts = Post.objects.filter(user=obj)
        return [post.id for post in posts]

    def get_userFollowerCount(self, obj):
        return obj.followers.count()

    def get_userFollowingCount(self, obj):
        return obj.following.count()

    def get_userFriendCount(self, obj):
        return obj.get_friends().count()

    def get_userFollowerId(self,obj):
        """Method to get the list of follower's ids related to the user"""
        return [follower.id for follower in obj.followers.all()]

    def get_userFollowingId(self,obj):
        """Method to get the list of follower's ids related to the user"""
        return [following.id for following in obj.following.all()]

    def get_userLikeCount(self,obj):
        """Method to get the total number of likes related tot he user's posts"""
        return sum(post.postLike.count() for post in obj.posts.all())


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    userEmailAddress = serializers.EmailField()
    password = serializers.CharField(
        style = {"input_type": "password"},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        userEmailAddress = attrs.get("userEmailAddress")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"),
            username=userEmailAddress,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs

class UserProfileImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to user profile"""
    class Meta:
        model = User
        fields = ["id", "userProfilePictureUrl"]
        read_only_fields = ["id"]
        extra_kwargs = {"userProfilePictureUrl": {"required":"True"}}

class UserProfileCoverSerializer(serializers.ModelSerializer):
    """Serializer for uploading cover picture to user profile"""
    class Meta:
        model = User
        fields = ["id", "userCoverPictureUrl"]
        read_only_fields = ["id"]
        extra_kwargs = {"userCoverPictureUrl": {"required":"True"}}

class UsersListSerializer(serializers.ModelSerializer):
    """Serializer for retrieving a list of users"""
    userId = serializers.ReadOnlyField(source="id")
    class Meta:
        model = User
        fields = ["userId", "userUsername", "userName","IPv4", "userProfilePictureUrl"]


