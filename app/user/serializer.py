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
    userIPAddress = serializers.SerializerMethodField()
    userPostId = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ["email",
                  "password",
                  "username",
                  "name",
                  "userPhoneNumber",
                  "userBio",
                  "userProfilePictureUrl",
                  "userBirthDate",
                  "userAccountRegisterDate",
                  "userIPAddress",
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
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

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

    def get_userIPAddress(self, obj):
        """Return the user's IP address"""
        request = self.context.get("request")
        ip_address = self.context.get("ip_address")
        if ip_address:
            return ip_address
        elif request:
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get("REMOTE_ADDR")
            return ip
        return None

    def get_userPostId(self,obj):
        """Method to get the list of postId related to the user"""
        #return Post.objects.filter(user=obj).values_list('id', flat=True)
        posts = Post.objects.filter(user=obj)
        return [post.id for post in posts]

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style = {"input_type": "password"},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"),
            username=email,
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


