"""
Views for the post APIs.
"""

from rest_framework import viewsets,status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Post, PostLike, User
from post import serializers


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
        serializer.save(user=self.request.user, postPublishIpAddress=postPublishIpAddress)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to post"""
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False, methods = ["GET"], url_path="following")
    # def following(self, request):
    #     user = self.request.user
    #     queryset = Post.objects.filter(user__in = user.following.all()).order_by('-postPublishDateTime')
    #     page = self.paginate_queryset(queryset)

    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=False, methods = ["GET"], url_path="for-you")
    # def all_posts(self, request):
    #     """Retrieve all posts"""
    #     user = self.request.user
    #     queryset = Post.objects.exclude(user=user).order_by("-postPublishDateTime")
    #     page = self.paginate_queryset(queryset)

    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=["GET"], url_path="for-you/(?P<id>\d+)")
    # def for_you_post(self, request, id=None):
    #     """Retrieve a single post for you"""
    #     try:
    #         post = Post.objects.get(pk=id)
    #     except Post.DoesNotExist:
    #         return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    #     serializer = self.get_serializer(post)
    #     return Response(serializer.data, status=status.HTTP_200_OK)


# class LikePostView(generics.GenericAPIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         post_id = kwargs.get('post_id')
#         try:
#             post = Post.objects.get(pk=post_id)
#         except Post.DoesNotExist:
#             return Response({"detail": "Post not found"})
#         user = request.user

#         if user in post.postLike.all():
#             post.postLike.remove(user)
#             return Response({"message": "Post unliked"}, status=status.HTTP_200_OK)
#         else:
#             post.postLike.add(user)
#             return Response({"message": "Post liked"}, status=status.HTTP_200_OK)

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
        existing_like = PostLike.objects.filter(user=user, post=post).order_by("-likeDateTime").first()
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

# class PostLikesListView(generics.ListAPIView):
#     serializer_class = serializers.UsersListSerializer
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         post_id = self.kwargs["post_id"]
#         try:
#             post = Post.objects.get(pk=post_id)
#         except Post.DoesNotExist:
#             return Response({"detail": "Post not found"})
#         return post.postLike.all()

class PostLikedUsersListView(generics.ListAPIView):
      serializer_class = serializers.UsersListSerializer
      authentication_classes = [TokenAuthentication]
      permission_classes = [IsAuthenticated]

      def get_queryset(self):
          """return a list of all of the users who liked  a particular post"""
          post_id = self.kwargs["post_id"]
          liked_users_ids = PostLike.objects.filter(post_id=post_id, isActive=True).values_list("user_id", flat=True)
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

    def get_queryset(self):
        """
        This view should return a list of all the posts that have been
        liked by the currently authenticated user.
        """
        user_id = self.request.user.id
        liked_posts_ids = PostLike.objects.filter(user_id=user_id, isActive=True).values_list("post_id",flat=True)
        return Post.objects.filter(id__in=liked_posts_ids)

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
