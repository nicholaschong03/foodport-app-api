"""
URL mappings for the user API
"""

from django.urls import path
from user import views

app_name = "user"

urlpatterns = [
    path("user/signup/", views.CreateUserView.as_view(), name="create"),
    path("user/login/", views.CreateTokenView.as_view(), name="token"),
    path("user/me/", views.ManagerUserView.as_view(), name="me"),
    path("user/logout/", views.LogoutView.as_view(), name="logout"),
    path("user/upload-profile-image/", views.UploadProfileImageView.as_view(), name="upload_profile_image"),
    path("user/<int:id>/", views.RetrieveUserView.as_view(), name="other_user"),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/follow/<int:user_id>/", views.FollowUserView.as_view(), name="follow_user"),
    path("user/<int:user_id>/followers", views.FollowersListView.as_view(), name = "followers_list"),
    path("user/<int:user_id>/following", views.FollowingListView.as_view(), name = "following_list"),
    ]
