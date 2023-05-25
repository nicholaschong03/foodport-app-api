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

from ip2geotools.databases.noncommercial import DbIpCity



class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""
    IPv4 = serializers.SerializerMethodField()
    userPostId = serializers.SerializerMethodField()
    userId = serializers.ReadOnlyField(source="id")
    userFollowerCount = serializers.SerializerMethodField()
    userFollowingCount = serializers.SerializerMethodField()
    userFriendsCount = serializers.SerializerMethodField()
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
                  "userFriendsCount",
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

    # def get_userIPAddress(self, obj):
    #     """Return the user's IP address"""
    #     request = self.context.get("request")
    #     ip_address = self.context.get("ip_address")
    #     if ip_address:
    #         return ip_address
    #     elif request:
    #         x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    #         if x_forwarded_for:
    #             ip = x_forwarded_for.split(',')[0]
    #         else:
    #             ip = request.META.get("REMOTE_ADDR")
    #         return ip
    #     return None
    def get_IPv4(self, obj):
        """Return the user's IP address and location"""
        request = self.context.get("request")
        ip_address = self.context.get("ip_address")
        if not ip_address and request:
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get("REMOTE_ADDR")

        if ip_address:
            try:
                response = DbIpCity.get(ip_address, api_key='free')
                return {
                    "ipAddress": ip_address,
                    "location": {
                        "city": response.city,
                        "region": response.region,
                        "country": response.country,
                    }
                }
            except Exception as e:
                # Handle any exceptions that arise from the IP lookup
                return {
                    "ipAddress": ip_address,
                    "location": str(e)
                }

        return None

    # def get_IPv4(self, obj):
    #     """Return the user's IP address"""
    #     #request = self.context.get("request")
    #     ip_address = self.context.get("ip_address")
    #     location = self.context.get("location")

    #     if ip_address and location:
    #         return {
    #             "ipAddress": ip_address,
    #             "location": location,
    #         }
    #     elif ip_address:
    #         return {
    #             "ipAddress": ip_address,
    #             "location": "N/A"
    #         }
    #     else:
    #         return{
    #             "ipAddress": "N/A",
    #             "location": "N/A"
    #         }

    def get_userPostId(self,obj):
        """Method to get the list of postId related to the user"""
        posts = Post.objects.filter(user=obj)
        return [post.id for post in posts]

    def get_userFollowerCount(self, obj):
        return obj.followers.count()

    def get_userFollowingCount(self, obj):
        return obj.following.count()

    def get_userFriendsCount(self, obj):
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
        fields = ["userId", "userUsername", "userName", "userProfilePictureUrl"]


