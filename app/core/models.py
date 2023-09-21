"""
Database models.
"""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models, IntegrityError
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.validators import UniqueValidator

import uuid
import os

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from imagekit.processors import Adjust

from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO

import sys


def post_image_file_path(instance, filename):
    """Genrate file path for new post image."""
    ext = os.path.splitext(filename)[1]
    if ext == ".jpg" or ext == ".png" or ext == ".jpeg":
        user_directory_path = f"uploads/posts/user{instance.user.id}/images"
    elif ext == ".mp4" or ext == ".avi":
        user_directory_path = f"uploads/posts/user{instance.user.id}/videos"
    filename = f"{uuid.uuid4()}{ext}"
    return os.path.join(user_directory_path, filename)


def user_image_file_path(instance, filename):
    """Generate file path for profile"""
    ext = os.path.splitext(filename)[1]
    directory_path = f"uploads/profiles/user{instance.id}/picture"
    filename = f"{uuid.uuid4()}{ext}"
    return os.path.join(directory_path, filename)


def user_cover_picture_file_path(instance, filename):
    """Generate file path for profile"""
    ext = os.path.splitext(filename)[1]
    directory_path = f"uploads/profiles/user{instance.id}/cover-picture"
    filename = f"{uuid.uuid4()}{ext}"
    return os.path.join(directory_path, filename)


class UserManager(BaseUserManager):
    """Manager for user."""

    def _generate_unique_username(self):
        """Generating a unique username by checking against existing usernames"""
        while True:
            username = str(uuid.uuid4())[:8]
            if not self.model.objects.filter(userUsername=username).exists():
                return username

    def create_user(self, userEmailAddress, firebase_uid=None, userUsername="", password=None, **extra_field):
        """Create, save and return a new user"""
        if not userEmailAddress:
            raise ValueError("User must have an email address")
        if not userUsername:
            userUsername = self._generate_unique_username()
        user = self.model(userEmailAddress=self.normalize_email(
            userEmailAddress), userUsername=userUsername, firebase_uid=firebase_uid, **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, userEmailAddress, password):
        """Create and return a new superuser."""
        user = self.create_user(
            userEmailAddress=userEmailAddress, password=password, userUsername="admin")
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

        return user


class NullablePhoneNumberField(PhoneNumberField):
    """Allow userPhoneNumber field to be null and unique"""

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        return value if value else None


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    userEmailAddress = models.EmailField(max_length=255, unique=True)
    firebase_uid = models.CharField(max_length=255, unique=True, null=True)
    userName = models.CharField(max_length=255, blank=True)
    userPhoneNumber = NullablePhoneNumberField(
        unique=True, blank=True, null=True)
    userUsername = models.CharField(max_length=255, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    userBio = models.TextField(blank=True)
    userProfilePictureUrl = models.ImageField(
        null=True, upload_to=user_image_file_path)

    userBirthDate = models.DateField(blank=True, null=True)
    userAccountRegisterDate = models.DateTimeField(auto_now_add=True)
    userPostLike = models.JSONField(default=dict, blank=True)
    userPostComment = models.JSONField(default=dict, blank=True)
    userPostSave = models.JSONField(default=dict, blank=True)
    userPostShare = models.JSONField(default=dict, blank=True)
    userPostView = models.JSONField(default=dict, blank=True)
    userPostCommentView = models.JSONField(default=dict, blank=True)
    userPostDishVisit = models.JSONField(default=dict, blank=True)
    userPostDishSellerVisit = models.JSONField(default=dict, blank=True)
    userLikes = models.IntegerField(blank=True, null=True)
    userFollowers = models.IntegerField(blank=True, null=True)
    userFollowing = models.IntegerField(blank=True, null=True)
    userFriend = models.IntegerField(default=0)
    userAge = models.IntegerField(blank=True, null=True)
    following = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers", blank=True)
    userGender = models.CharField(max_length=255, blank=True)
    userLocation = models.JSONField(default=dict, blank=True)
    userShowBirthDate = models.BooleanField(default=True)
    userCoverPictureUrl = models.ImageField(
        null=True, upload_to=user_cover_picture_file_path)
    IPv4 = models.JSONField(default=dict, null=True, blank=True)
    userLatitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)
    userLongitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)

    # def save(self, *args, **kwargs):
    #     # Storing the old file paths before calling super().save()
    #     if self.pk:
    #         old_instance = User.objects.get(pk=self.pk)
    #         old_profile_pic = old_instance.userProfilePictureUrl.path if old_instance.userProfilePictureUrl else None
    #         old_cover_pic = old_instance.userCoverPictureUrl.path if old_instance.userCoverPictureUrl else None
    #     else:
    #         old_profile_pic = None
    #         old_cover_pic = None

    #     super().save(*args, **kwargs)

    #     # Handle UserProfilePictureUrl
    #     if self.userProfilePictureUrl and hasattr(self.userProfilePictureUrl, 'file'):
    #         # Deleting the old file if it exists
    #         if old_profile_pic and os.path.exists(old_profile_pic):
    #             os.remove(old_profile_pic)

    #         # Your existing image handling code
    #         img = Image.open(self.userProfilePictureUrl)
    #         img = img.convert('RGB')
    #         img = img.resize((800, 800), Image.ANTIALIAS)
    #         buffer = BytesIO()
    #         img.save(buffer, format='JPEG', quality=85)
    #         buffer.seek(0)
    #         self.userProfilePictureUrl.save(name=self.userProfilePictureUrl.name, content=ContentFile(buffer.read()), save=False)

    #     # Handle UserCoverPictureUrl
    #     if self.userCoverPictureUrl and hasattr(self.userCoverPictureUrl, 'file'):
    #         # Deleting the old file if it exists
    #         if old_cover_pic and os.path.exists(old_cover_pic):
    #             os.remove(old_cover_pic)

    #         # Your existing image handling code
    #         img = Image.open(self.userCoverPictureUrl)
    #         img = img.convert('RGB')
    #         img = img.resize((800, 800), Image.ANTIALIAS)
    #         buffer = BytesIO()
    #         img.save(buffer, format='JPEG', quality=85)
    #         buffer.seek(0)
    #         self.userCoverPictureUrl.save(name=self.userCoverPictureUrl.name, content=ContentFile(buffer.read()), save=False)

    #     super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Store the old image paths before saving the new images
        if self.pk:
            old_instance = User.objects.get(pk=self.pk)
            old_profile_pic_path = old_instance.userProfilePictureUrl.path if old_instance.userProfilePictureUrl else None
            old_cover_pic_path = old_instance.userCoverPictureUrl.path if old_instance.userCoverPictureUrl else None
        else:
            old_profile_pic_path = None
            old_cover_pic_path = None

        profile_pic_modified = False
        cover_pic_modified = False
        super(User, self).save(*args, **kwargs)

        if self.userProfilePictureUrl and hasattr(self.userProfilePictureUrl, 'file'):
            # Open the image using Pillow
            img = Image.open(self.userProfilePictureUrl)

            # Resize the image.
            img = img.resize((1290, 1290), Image.ANTIALIAS)

            # Save the image back to userProfilePictureUrl
            buffer = BytesIO()
            img.save(fp=buffer, format="JPEG", quality=85)
            buffer.seek(0)
            self.userProfilePictureUrl.save(
                name=self.userProfilePictureUrl.name, content=ContentFile(buffer.read()), save=False)

            profile_pic_modified = True

        if self.userCoverPictureUrl and hasattr(self.userCoverPictureUrl, 'file'):
            # Open the image using Pillow
            img = Image.open(self.userCoverPictureUrl)

            # Resize the image.
            img = img.resize((1290, 1290), Image.ANTIALIAS)

            # Save the image back to userCoverPictureUrl
            buffer = BytesIO()
            img.save(fp=buffer, format="JPEG", quality=85)
            buffer.seek(0)
            self.userCoverPictureUrl.save(name=self.userCoverPictureUrl.name, content=ContentFile(
                buffer.read()), save=False)  # Corrected this line

            cover_pic_modified = True

        if profile_pic_modified or cover_pic_modified:
            # Call the "real" save() method once if any image field was modified
            super(User, self).save(*args, **kwargs)

        # Delete the old image files from the filesystem
        if old_profile_pic_path and profile_pic_modified:
            if os.path.exists(old_profile_pic_path):
                os.remove(old_profile_pic_path)
        if old_cover_pic_path and cover_pic_modified:
            if os.path.exists(old_cover_pic_path):
                os.remove(old_cover_pic_path)

    def get_friends(self):
        """Return a QuerySet of friends of the user"""
        return self.following.filter(following__in=[self])

    objects = UserManager()

    USERNAME_FIELD = "userEmailAddress"


class Business(models.Model):
    "Business object"
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    businessName = models.CharField(max_length=255)
    businessOperatingLocation = models.JSONField(null=True, blank=True)
    businessOperatingTime = models.JSONField(null=True, blank=True)
    businessVerified = models.BooleanField(default=False)
    businessSafeFood = models.BooleanField(default=False)
    businessHalal = models.BooleanField(default=False)
    sellerId = models.IntegerField(null=True, blank=True)
    businessInfoContributor = models.JSONField(null=True, blank=True)
    businessOperatingLatitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)
    businessOperatingLongitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)
    businessTrendRanking = models.IntegerField(null=True, blank=True)
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="following_businesses", blank=True
    )

    def __str__(self):
        return self.businessName

    # def get_all_menu_item_ids(self):
    #     return self.menuItemId or []


class MenuItem(models.Model):
    """Menu object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    dishInfoContributor = models.JSONField(default=dict, blank=True, null=True)
    sellerId = models.IntegerField(null=True, blank=True)
    business = models.ForeignKey(
        Business, on_delete=models.SET_NULL, null=True, blank=True, related_name="menu_items")
    category = models.CharField(max_length=255)

    basicIngredient = models.JSONField(default=list, blank=True, null=True)
    compositeIngredient = models.JSONField(default=list, blank=True, null=True)
    nutritionFacts = models.JSONField(default=dict, blank=True, null=True)
    # menuItemTotalPostCount = models.IntegerField(default=0)

    trendingPosition = models.IntegerField(null=True, blank=True)
    trendingDirection = models.CharField(max_length=255, null=True, blank=True)

    # def update_post_count(self):
    #     self.menuItemTotalPostCount = self.posts.count()
    #     self.save()

    def __str__(self):
        return self.name


class Post(models.Model):
    """Post object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    postReview = models.TextField()
    postPublishDateTime = models.DateTimeField(auto_now_add=True)
    postRatingDelicious = models.FloatField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=False,
        error_messages={"blank": "Please provide a rating from 1 to 5"})
    postRatingEatAgain = models.FloatField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=False,
        error_messages={"blank": "Please provide a rating from 1 to 5"})
    postRatingWorthIt = models.FloatField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=False,
        error_messages={"blank": "Please provide a rating from 1 to 5"})
    postPublishIpAddress = models.GenericIPAddressField(null=True, blank=True)
    postPhotoUrl = models.ImageField(null=True, upload_to=post_image_file_path)
    postView = models.JSONField(default=dict, blank=True)
    postComment = models.JSONField(default=dict, blank=True)
    postCommentView = models.JSONField(default=dict, blank=True)
    postSave = models.JSONField(default=dict, blank=True)
    postShare = models.JSONField(default=dict, blank=True)
    postDishSellerVisit = models.JSONField(default=dict, blank=True)
    postDishVisit = models.JSONField(default=dict, blank=True)
    postLikeCount = models.IntegerField(default=0)
    menuItem = models.ForeignKey(
        MenuItem, null=True, blank=True, related_name="posts", on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        # Call the "real" save() method
        super(Post, self).save(*args, **kwargs)

        if self.postPhotoUrl and hasattr(self.postPhotoUrl, 'file'):

            # Open the image using Pillow
            img = Image.open(self.postPhotoUrl)

            # Resize the image.
            img = img.resize((1290, 1290), Image.ANTIALIAS)

            # Save the image back to postPhotoUrl
            buffer = BytesIO()
            img.save(fp=buffer, format="JPEG", quality=85)
            buffer.seek(0)
            self.postPhotoUrl.save(
                name=self.postPhotoUrl.name, content=ContentFile(buffer.read()), save=False)

            # Call the "real" save() method again
            super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.postReview


class PostLike(models.Model):
    user = models.ForeignKey(User, related_name="likes",
                             on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="likes",
                             on_delete=models.CASCADE)
    isActive = models.BooleanField(default=True)
    likeDateTime = models.DateTimeField(auto_now_add=True)
    likeIpAddress = models.GenericIPAddressField(null=True, blank=True)
    likeUserAgent = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        post = self.post
        like_count = PostLike.objects.filter(post=post, isActive=True).count()
        unlike_count = PostLike.objects.filter(
            post=post, isActive=False).count()
        post.postLikeCount = like_count - unlike_count
        post.save()


class PostSave(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name="saves",
                             on_delete=models.CASCADE)
    postIsSaved = models.BooleanField(default=False)
    savedDateTime = models.DateTimeField(null=True, blank=True)
    unsavedDateTime = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "post")


class PostView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_views")
    viewDateTime = models.DateTimeField(auto_now_add=True)
    viewUserAgent = models.TextField(null=True, blank=True)


class PostComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments")
    commentContent = models.TextField()
    commentPublishDateTime = models.DateTimeField(auto_now_add=True)
    commentPublishIpAddress = models.GenericIPAddressField(
        null=True, blank=True)
    commentUserAgent = models.TextField(null=True, blank=True)
    commentLikes = models.JSONField(blank=True, null=True, default=list)
    commentReplies = models.JSONField(blank=True, null=True, default=list)
    commentPublishLastUpdatedDateTime = models.DateTimeField(
        null=True, blank=True)
    commentPublishLocation = models.JSONField(
        default=dict, null=True, blank=True)
    commentLikeCount = models.IntegerField(default=0)


class CommentLike(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_likes")
    comment = models.ForeignKey(
        PostComment, on_delete=models.CASCADE, related_name="likes")
    isActive = models.BooleanField(default=True)
    likeDateTime = models.DateTimeField(auto_now_add=True)
    likeIpAddress = models.GenericIPAddressField(null=True, blank=True)
    likeUserAgent = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        comment = self.comment
        like_count = CommentLike.objects.filter(
            comment=comment, isActive=True).count()
        unlike_count = CommentLike.objects.filter(
            comment=comment, isActive=False).count()
        comment.commentLikeCount = like_count - unlike_count
        comment.save()


class PostShare(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    sharedBy = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shared_post")
    sharedTo = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_post")
    sharedDateTime = models.DateTimeField(auto_now_add=True)


class Seller(models.Model):
    """Seller object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    sellerBusinessName = models.CharField(max_length=255)
    sellerOperatingLocation = models.JSONField(null=True, blank=True)
    sellerOperatingTime = models.JSONField(null=True, blank=True)
    sellerVerified = models.BooleanField(default=False)
    sellerSafeFood = models.BooleanField(default=False)
    sellerHalal = models.BooleanField(default=False)
    sellerOwnerId = models.IntegerField(null=True, blank=True)
    sellerInfoContributor = models.JSONField(null=True, blank=True)
    menuItemId = models.JSONField(blank=True, null=True, default=list)

    def __str__(self):
        return self.sellerBusinessName


class Dish(models.Model):
    """Dish object"""
    dishName = models.CharField(max_length=255)
    dishPrice = models.DecimalField(max_digits=10, decimal_places=2)
    dishMainIngredient = models.TextField(blank=True)
    dishIngredient = models.TextField(blank=True)
    dishNutrition = models.TextField(blank=True)
    # seller = models.ForeignKey(
    #     Seller,
    #     on_delete=models.CASCADE
    # )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )
    sellerId = models.IntegerField(null=True, blank=True)
    postId = models.JSONField(null=True, blank=True, default=list)
    dishInfoContributor = models.JSONField(default=dict, blank=True)
