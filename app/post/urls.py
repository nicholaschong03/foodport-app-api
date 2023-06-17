"""
URL mappings for the post app
"""

from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from post import views

router = DefaultRouter()
router.register("posts/user", views.PostViewset)

app_name = "post"

urlpatterns = [
    path("", include(router.urls)),
    path("like/post/<int:post_id>/", views.LikePostView.as_view(),  name="like-post"),
    # path("<int:post_id>/likes/", views.PostLikesListView.as_view(), name="post-likes"),
    path("posts/following/", views.FollowingPostsView.as_view(), name="following-post"),
    path("posts/for-you/", views.AllPostsView.as_view(), name =  "for-you-post"),
    path("posts/feed/for-you/", views.SearchFilterPostsView.as_view(), name= "for-you-post-feed"),
    path("posts/", views.SearchFilterPostsView.as_view(), name= "posts-search-filter"),
    path("post/<int:pk>/", views.SinglePostView.as_view(), name="single-post"),
    path("postlike/<int:post_id>/", views.PostLikeListView.as_view(), name="postlike-list"),
    path("posts/liked/", views.UserlikedPostsListView.as_view(), name="liked-post-list"),
    path("posts/<int:post_id>/liked/users/", views.PostLikedUsersListView.as_view(), name="post-liked-users-list"),
    path("posts/user/", views.SearchFilterPostsView.as_view(), name="search-filter-post"),
    path("posts/review-rating/menuItem/", views.ReturnRatingReviewPostsView.as_view(), name="review-rating-post"),

]
