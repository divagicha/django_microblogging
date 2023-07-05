import coreapi
import coreschema
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema, AutoSchema
from rest_framework.views import APIView

from blogging.constants import TIMELINE_TTL
from blogging.serializers import UserSerializer, PostSerializer, TimelineSerializer, \
    FollowUserSerializer
from blogging.models import Post, Followers
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


class FollowUserView(APIView):
    """
    Follows provided user_id, with logged-in user being the 'following' user
    """
    schema = ManualSchema(
        fields=[
            coreapi.Field(
                name="user_id",
                location='form',            # possible values: path, query, body, form
                required=True,
                schema=coreschema.Integer(description="user id to follow"),
                type=int,
                description='{"user_id": int}',
                example='',
            ),
        ],
        encoding='application/json'
    )

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
            except ValidationError:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        'status': 'failed',
                        'message': "invalid follow request",
                        'errors': {
                            'validation_errors': ["user and following user can't be same"]
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
    different accounts whom the user is following.
    """
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field(
                name="update_cache",
                location='query',            # possible values: path, query, body, form
                required=False,
                schema=coreschema.Boolean(description="whether to force update cache"),
                type=bool,
                description='',
                example='',
            ),
        ]
    )

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
