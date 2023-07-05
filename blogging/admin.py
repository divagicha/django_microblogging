from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from blogging.models import Post, PostInteraction, Followers

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'followers',
                    'following', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    @classmethod
    def followers(cls, obj):
        return obj.followers.filter(is_active=True).count()

    @classmethod
    def following(cls, obj):
        return obj.following.filter(is_active=True).count()


@admin.register(Followers)
class FollowersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'following_user', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)


class PostCommentFilter(SimpleListFilter):
    title = _('Type')
    parameter_name = 'type'

    def lookups(self, request, model_admin):
        # This is where we create filter options; we have two
        return [('post', 'Post'), ('comment', 'Comment')]

    def queryset(self, request, queryset):
        if self.value() == 'post':
            return queryset.filter(parent__isnull=True)
        elif self.value() == 'comment':
            return queryset.filter(parent__isnull=False)

        return queryset


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'headline', 'parent', 'is_active', 'is_deleted', 'created_at',
                    'updated_at')
    raw_id_fields = ('parent',)
    readonly_fields = ('slug',)
    list_filter = (PostCommentFilter, 'is_active')


@admin.register(PostInteraction)
class PostInteractionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'activity', 'created_at')
    list_filter = ('activity',)
