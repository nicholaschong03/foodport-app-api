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
    """Genrate file path for new recipe image."""
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"

    return os.path.join("uploads", "post", filename)



class UserManager(BaseUserManager):
    """Manager for user."""

    def create_user(self, email, username="", password=None, **extra_field):
        """Create, save and return a new user"""
        if not email:
            raise ValueError("User must have an email address")
        if not username:
            raise ValueError("User must have a username")
        user = self.model(email=self.normalize_email(email), username=username, **extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email=email, password=password, username="admin")
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True)
    # phone_num = PhoneNumberField(unique=True, blank=True, null=True,
    #                             validators=[UniqueValidator(message="Phone Number already exists.")])
    phone_num = PhoneNumberField(unique=True, blank=True, null=True)
    username = models.CharField(max_length=255, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"


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
    postPublishIpAddress = models.CharField(max_length=255, blank=True)
    dishId= models.CharField(max_length=255, blank=True)
    userId = models.CharField(max_length=255, blank=True)
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
