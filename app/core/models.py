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
    """Generate file path for new """
    ext = os.path.splitext(filename)[1]
    directory_path = f"uploads/profiles/user{instance.id}/picture"
    filename = f"{uuid.uuid4()}{ext}"
    return os.path.join(directory_path, filename)



class UserManager(BaseUserManager):
    """Manager for user."""

    def create_user(self, userEmailAddress, userUsername="", password=None, **extra_field):
        """Create, save and return a new user"""
        if not userEmailAddress:
            raise ValueError("User must have an email address")
        if not userUsername:
            raise ValueError("User must have a username")
        user = self.model(userEmailAddress=self.normalize_email(userEmailAddress), userUsername=userUsername, **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, userEmailAddress, password):
        """Create and return a new superuser."""
        user = self.create_user(userEmailAddress=userEmailAddress, password=password, userUsername="admin")
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    userEmailAddress = models.EmailField(max_length=255, unique=True)
    userName = models.CharField(max_length=255, blank=True)
    userPhoneNumber = PhoneNumberField(unique=True, blank=True, null=True)
    userUsername = models.CharField(max_length=255, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    userBio = models.TextField(blank=True)
    userProfilePictureUrl = models.ImageField(null=True, upload_to=user_image_file_path)
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




    objects = UserManager()

    USERNAME_FIELD = "userEmailAddress"


class Post(models.Model):
    """Post object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
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
    dishId= models.IntegerField(null=True, blank=True, default=0)
    postPhotoUrl = models.ImageField(null=True, upload_to=post_image_file_path)
    postView = models.JSONField(default=dict, blank=True)
    postLike = models.JSONField(default=dict, blank=True)
    postComment = models.JSONField(default=dict, blank=True)
    postCommentView = models.JSONField(default=dict, blank=True)
    postSave = models.JSONField(default=dict, blank=True)
    postShare = models.JSONField(default=dict, blank=True)
    postDishSellerVisit = models.JSONField(default=dict, blank=True)
    postDishVisit = models.JSONField(default=dict, blank=True)



    def __str__(self):
        return self.postReview
