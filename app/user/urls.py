"""
URL mappings for the user API
"""

from django.urls import path
from user import views

app_name = "user"

urlpatterns = [
    path("signup/", views.CreateUserView.as_view(), name="create"),
    path("login/", views.CreateTokenView.as_view(), name="token"),
    path("me/", views.ManagerUserView.as_view(), name="me"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("upload-profile-image/", views.UploadProfileImageView.as_view(), name="upload_profile_image"),
    path("<int:id>/", views.RetrieveUserView.as_view(), name="other_user"),
    ]
