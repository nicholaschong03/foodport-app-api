"""
Views for the post APIs.
"""

from rest_framework import viewsets, status, generics, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone

from PIL import Image
from io import BytesIO
from django.core.files import File

from core.models import Post, PostLike, User, PostSave, PostView, PostComment, PostShare
from post import serializers

from django.db.models import Max, Case, When, BooleanField


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

channel_layer = get_channel_layer()


class PostViewset(viewsets.ModelViewSet):
    """View for manage post APIs. """
    serializer_class = serializers.PostDetailSerializer
    queryset = Post.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve posts for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == "list":
            return serializers.PostSerializer
        elif self.action == "upload_image":
            return serializers.PostImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new post"""
        postPublishIpAddress = self.request.META.get("REMOTE_ADDR")
        serializer.save(user=self.request.user,
                        postPublishIpAddress=postPublishIpAddress)
        image = self.request.data.get("postPhotoUrl")
        if image:
            # open image
            img = Image.open(image)

        # resize image
            img.thumbnail((800, 600), Image.ANTIALIAS)

        # save image back to image field
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=50)

            image_file = File(thumb_io, name=image.name)
            serializer.save(user=self.request.user,
                            postPublishIpAddress=postPublishIpAddress,
                            postPhotoUrl=image_file)
        else:
            serializer.save(user=self.request.user,
                            postPublishIpAddress=postPublishIpAddress)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to post"""
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomPostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class LikePostView(generics.GenericAPIView):
    """this view is for users to like a post"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PostLikeSerializer

    def post(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found"})
        user = request.user
        data = {
            "user": user.id,
            "post": post.id,
            "likeIpAddress": request.META.get("REMOTE_ADDR"),
            "likeUserAgent": request.META.get("HTTP_USER_AGENT"),
        }
        existing_like = PostLike.objects.filter(
            user=user, post=post).order_by("-likeDateTime").first()
        if existing_like and existing_like.isActive == True:
            data["isActive"] = False
            response_data = {"isLiked": False}
        else:
            data["isActive"] = True
            response_data = {"isLiked": True}

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(response_data, status=status.HTTP_200_OK)


class PostLikedUsersListView(generics.ListAPIView):
    serializer_class = serializers.UsersListSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """return a list of all of the users who liked  a particular post"""
        post_id = self.kwargs["post_id"]
        liked_users_ids = PostLike.objects.filter(
            post_id=post_id, isActive=True).values_list("user_id", flat=True)
        return User.objects.filter(id__in=liked_users_ids)


class PostLikeListView(generics.ListAPIView):
    serializer_class = serializers.PostLikeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """This view should return a list of all the
           PostLikes for the currently authenticated user
        """
        post_id = self.kwargs["post_id"]
        return PostLike.objects.filter(post_id=post_id)


class UserlikedPostsListView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the posts that have been
        liked by the currently authenticated user.
        """
        user_id = self.request.user.id
        # Annotate PostLike objects with the maximum likeDateTime for each post.
        post_likes = PostLike.objects.filter(user_id=user_id).values(
            "post").annotate(max_likeDateTime=Max("likeDateTime"))
        # Filter for the PostLike objects that match the maximum likeDateTime and have isActive=True.
        liked_posts_ids = [post_like["post"] for post_like in post_likes if PostLike.objects.filter(
            post_id=post_like["post"], likeDateTime=post_like["max_likeDateTime"], isActive=True).exists()]
        return Post.objects.filter(id__in=liked_posts_ids)


class SavePostView(generics.GenericAPIView):
    """This view is for users to save a post"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PostSaveSerializer

    def post(self, request, post_id):
        user = request.user
        post_save, created = PostSave.objects.get_or_create(
            user=user, post_id=post_id)

        # Check if post is already saved
        post_save.postIsSaved = not post_save.postIsSaved
        if post_save.postIsSaved:
            post_save.savedDateTime = timezone.now()
            post_save.unsavedDateTime = None

        else:
            post_save.unsavedDateTime = timezone.now()

        post_save.save()
        return Response({"status": "Saved" if post_save.postIsSaved else "Unsaved"}, status=status.HTTP_200_OK)


class ListSavedPostView(generics.ListAPIView):
    """This view is for users to view the saved posts"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PostSerializer

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(saves__user=user, saves__postIsSaved=True)


class ViewPostView(generics.GenericAPIView):
    """This view is to create a postView instance"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PostViewSerializer

    def post(self, request, *args, **kwargs):
        post_id = kwargs.get("post_id")
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found"})
        user = request.user
        data = {
            "user": user.id,
            "post": post.id,
            "viewUserAgent": request.META.get("HTTP_USER_AGENT"),
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "Viewed"}, status=status.HTTP_200_OK)


class PostViewListView(generics.ListAPIView):
    serializer_class = serializers.PostViewSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """This view will return a list of all the postViews"""
        post_id = self.kwargs["post_id"]
        return PostView.objects.filter(post_id=post_id)


class CretePostCommentView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    serializer_class = serializers.PostCommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get("post_id")
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found"})
        serializer.save(
            user=self.request.user,
            post=post,
            commentIpAddress=self.request.META.get("REMOTE_ADDR"),
            commentUserAgent=self.request.META.get("HTTP_USER_AGENT")

        )
        # return Response({"status":"commented"}, status=status.HTTP_200_OK)


class ListPostCommentView(generics.ListAPIView):
    """This view is for users to view the comments of a post"""
    serializer_class = serializers.PostCommentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        return PostComment.objects.filter(post_id=post_id).order_by("-commentDateTime")


class DeleteCommentView(generics.DestroyAPIView):
    """This view is for users to delete their comment"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PostCommentSerializer
    queryset = PostComment.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "Not authorized to delete this comment."}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowingPostsView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(user__in=user.following.all()).order_by('-postPublishDateTime')


class AllPostsView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Post.objects.exclude(user=user).order_by("-postPublishDateTime")


class SinglePostView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class SearchFilterPostsView(generics.ListAPIView):
    serializer_class = serializers.PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["menuItemId", "user"]
    pagination_class = CustomPostPagination
    queryset = Post.objects.all().order_by("postPublishDateTime")


    def get_queryset(self):
        user = self.request.user

        # Annotate each post with an is_viewed field
        queryset = Post.objects.annotate(
            is_viewed=Case(
                When(post_views__user=user, then=True),
                default=False,
                output_field=BooleanField()
            )
        )

        # Order by unseen post first, and then post
        queryset = queryset.order_by("is_viewed", "-postPublishDateTime")

        return queryset


class ReturnRatingReviewPostsView(generics.ListAPIView):
    serializer_class = serializers.PostReviewRatingSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Post.objects.all().order_by("-postRatingEatAgain",
                                           "-postRatingWorthIt", "-postRatingDelicious")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["menuItemId"]
    pagination_class = CustomPostPagination


class ReturnHighestEatAgainRatingReview(generics.ListAPIView):
    serializer_class = serializers.PostReviewRatingSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Post.objects.all().order_by("-postRatingEatAgain")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["menuItemId"]
    pagination_class = CustomPostPagination


class ReturnHighestWorthItRatingReview(generics.ListAPIView):
    serializer_class = serializers.PostReviewRatingSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Post.objects.all().order_by("-postRatingWorthIt")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["menuItemId"]
    pagination_class = CustomPostPagination


class ReturnHighestDeliciousRatinReview(generics.ListAPIView):
    serializer_class = serializers.PostReviewRatingSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Post.objects.all().order_by("-postRatingDelicious")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["menuItemId"]
    pagination_class = CustomPostPagination


# def share_post_view(request, post_id, user_id):
#     # Retrieve the post and users from the database
#     try:
#         post = Post.objects.get(pk=post_id)
#     except Post.DoesNotExist:
#         return Response({"detail": "Post not found"}, status=404)

#     try:
#         shared_to = User.objects.get(pk=user_id)
#     except User.DoesNotExist:
#         return Response({"detail": "User not found"}, status=404)

#     shared_by = request.user

#     # Create the PostShare instance
#     serializer = serializers.PostShareSerializer(data={
#         "post": post.id,
#         "sharedBy": shared_by.id,
#         "sharedTo": shared_to.id
#     })

#     serializer.is_valid(raise_exception=True)
#     serializer.save()


#     # Send a WebSocket message to the shared_to user
#     async_to_sync(channel_layer.group_send)(
#         f"user_{shared_to.id}",
#         {
#             "type": "share.post",
#             "post_id": post.id,
#             "shared_by_username": shared_by.username,
#         }
#     )
#     return HttpResponse("Post shared successfully")

class SharePostView(generics.GenericAPIView):
    """This view is for user share the post"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PostShareSerializer


    def post(self, request, *args, **kwargs):
        post_id = kwargs.get("post_id")

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found"})

        user_id = kwargs.get("user_id")

        try:
            shared_to = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Post not found"})

        shared_by = request.user
        data = {
            "sharedBy": shared_by.id,
            "sharedTo": shared_to.id,
            "post" : post.id
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Send a WebSocket message to the shared_to user
        async_to_sync(channel_layer.group_send)(
            f"user_{shared_to.id}",
            {
                "type": "share.post",
                "post_id": post.id,
                "shared_by_username": shared_by.userName,
            }
        )
        return HttpResponse("Post shared successfully")