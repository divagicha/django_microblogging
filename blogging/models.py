from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from blogging.enums import Interaction


class Followers(models.Model):
    user = models.ForeignKey(User, related_name='followers', on_delete=models.PROTECT,
                             help_text="user being followed")
    following_user = models.ForeignKey(User, related_name='following', on_delete=models.PROTECT,
                                       help_text="user following another user")
    is_active = models.BooleanField(_("is currently following"), default=True,
                                    help_text="used to toggle follow/unfollow after once followed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} followed by {self.following_user.username}"

    def clean(self):
        if self.user == self.following_user:
            raise ValidationError("user and following_user can't be same")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'following_user')
        verbose_name = 'Follower'
        verbose_name_plural = 'Followers'


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             help_text="user who is creating the post")
    slug = models.CharField(max_length=128, null=False, blank=True, unique=True,
                            help_text="text pattern to uniquely identify a post/comment")
    headline = models.CharField(max_length=250, null=True, blank=True,
                                help_text="short text describing post")
    body = models.TextField(max_length=1000, null=False, blank=False,
                            help_text="actual content of the post")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="boolean indicating if actions "
                                                            "(like/comment/share/repost) can be "
                                                            "performed on the post")
    is_deleted = models.BooleanField(default=False, help_text="boolean indicating if post is "
                                                              "hidden from the platform")
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='comments',
        on_delete=models.PROTECT, help_text="if selected, indicates comment on the selected post"
    )

    def __str__(self):
        return f"{'POST' if not self.parent else 'COMMENT'} #{self.id} - {self.user.username}"

    def clean(self):
        if self.parent and self.headline:
            raise ValidationError(f"comment can't have headline")

        if self.parent and not self.is_active:
            raise ValidationError(f"can't post comment on an inactive post")

    def save(self, *args, **kwargs):
        if not self.parent:
            self.slug = slugify(self.body[:45])
        else:
            self.slug = f"thread-{self.parent.id}-comment-{self.id}"

        super(Post, self).save(*args, **kwargs)

    def get_comments(self):
        return self.comments.filter(is_active=True)

    def get_interactions(self, activity=None):
        if activity and Interaction.has_name(activity):
            return self.interactions.filter(activity=activity)

        return self.interactions.all()


class PostInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, help_text="user taking action on "
                                                                       "the post")
    post = models.ForeignKey(Post, related_name='interactions', on_delete=models.PROTECT)
    activity = models.CharField(choices=Interaction.choices(), max_length=20,
                                help_text="describes action taken on the post")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post} - {self.activity}(d) by {self.user.username}"

    def clean(self):
        if self.activity != Interaction.like.name and self.post.parent is not None:
            raise ValidationError("comments can only be liked and can't be shared or reposted")

        if not self.post.is_active:
            raise ValidationError(f"can't publish activity on an inactive post")
