from django.contrib.auth.models import User
from rest_framework import serializers

from blogging.enums import Interaction
from blogging.models import Post, Followers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'groups', 'followers', 'following')

    @classmethod
    def get_followers(cls, obj):
        return obj.followers.filter(is_active=True).count()

    @classmethod
    def get_following(cls, obj):
        return obj.following.filter(is_active=True).count()


class PostSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    share = serializers.SerializerMethodField()
    repost = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'user', 'headline', 'body', 'parent', 'is_active', 'is_deleted',
                  'created_at', 'updated_at', 'likes', 'comment', 'share', 'repost')

    @classmethod
    def get_likes(cls, obj):
        return obj.get_interactions(activity=Interaction.like.name).count()

    @classmethod
    def get_comment(cls, obj):
        return obj.get_comments().count()

    @classmethod
    def get_share(cls, obj):
        return obj.get_interactions(activity=Interaction.share.name).count()

    @classmethod
    def get_repost(cls, obj):
        return obj.get_interactions(activity=Interaction.repost.name).count()


class FollowUserSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        required=True, queryset=User.objects.all()
    )
    following_user = serializers.PrimaryKeyRelatedField(
        required=True, queryset=User.objects.all()
    )

    class Meta:
        model = Followers
        fields = '__all__'


class TimelineSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        write_only=True, required=True, queryset=User.objects.all()
    )
    posts = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('user', 'id', 'username', 'email', 'first_name', 'last_name', 'posts')

    @classmethod
    def get_posts(cls, obj):
        following_users = list(
            obj.following.filter(is_active=True).values_list('user_id', flat=True)
        )
        following_users.append(obj.id)
        posts = Post.objects.filter(user_id__in=following_users, parent__isnull=True,
                                    is_active=True, is_deleted=False).order_by('-updated_at')
        return PostSerializer(posts, many=True, read_only=True).data
