from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from blogging.constants import TIMELINE_TTL
from blogging.schemas import TimelineViewSchema, FollowUserViewSchema, PostInteractionViewSetSchema
from blogging.serializers import UserSerializer, PostSerializer, TimelineSerializer, \
    FollowUserSerializer, PostInteractionSerializer
from blogging.models import Post, Followers, PostInteraction
from core.redis_helper import RedisInterface


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed, created or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows posts to be viewed, created
    """
    queryset = Post.objects.filter(parent__isnull=True).order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]


class PostInteractionViewSet(viewsets.ViewSet):
    """
    API endpoint that allows posts interactions (like / share / repost) to be created,
    with logged-in user being the user interacting with post / comment
    """
    schema = PostInteractionViewSetSchema
    queryset = PostInteraction.objects.all().order_by('-created_at')
    serializer_class = PostInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, format=None):
        request_data = {
            **request.data,
            **{'user': request.user.id}
        }

        serializer = PostInteractionSerializer(data=request_data)

        if not serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'status': 'failed',
                    'message': "invalid post interaction request",
                    'errors': serializer.errors
                }
            )

        try:
            serializer.save()
            return Response(serializer.data)
        except ValidationError as exc:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'status': 'failed',
                    'message': "invalid post interaction request",
                    'errors': {
                        'validation_errors': [str(exc)]
                    }
                }
            )


class FollowUserView(APIView):
    """
    Follows provided user_id, with logged-in user being the 'following' user
    """
    schema = FollowUserViewSchema
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        followed_user = request.data.get('user_id')
        following_user = request.user

        data = {
            'user': followed_user,
            'following_user': following_user.id
        }
        
        serializer = FollowUserSerializer(data=data)

        follower = Followers.objects.filter(
            user_id=followed_user,
            following_user_id=following_user.id,
            is_active=False
        )
        if follower.exists():
            follower = follower.last()
            follower.is_active = True
            follower.save()
            return Response(FollowUserSerializer(follower).data)
        elif serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except ValidationError as exc:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        'status': 'failed',
                        'message': "invalid follow request",
                        'errors': {
                            'validation_errors': [str(exc)]
                        }
                    }
                )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'status': 'failed',
                    'message': "invalid follow request",
                    'errors': serializer.errors
                }
            )


class TimelineView(APIView):
    """
    Retrieve timeline of logged-in user.
    It consists of basic user profile details and a list of posts (chronologically arranged) from
    different accounts whom the user is following. (default cache TTL is 60 seconds)
    """
    schema = TimelineViewSchema
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def get_user(pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        # user = self.get_user(pk)
        user = request.user

        redis_conn = RedisInterface()
        update_cache = request.GET.get('update_cache', '')

        if redis_conn.get_redis_val(key=user.id) and not update_cache.lower() == 'true':
            return Response(redis_conn.get_redis_val(key=user.id))

        serializer = TimelineSerializer(user)

        redis_conn.set_redis_val(key=user.id, value=serializer.data, ttl=TIMELINE_TTL)
        return Response(serializer.data)
