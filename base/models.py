from datetime import date

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.urls import reverse


def user_upload_to(user, filename):
    return f"users/{user.username}/profile/{filename}"


class LowerCharField(models.CharField):
    def get_prep_value(self, value: str) -> str:
        return value and value.lower()


class User(AbstractUser):
    DEFAULT_COLOR = '#e30066'
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    photo = models.ImageField(_('user photo'), upload_to=user_upload_to,
                              default="defaults/default-user.png")
    birthday = models.DateField(_("birthday"), null=True, validators=[
                                MaxValueValidator(date.today,
                                                  _('Please choose correct birthday!')),])
    color = LowerCharField(_("color"), max_length=7, null=True, default=DEFAULT_COLOR,
                           validators=[RegexValidator(r'^#[A-fa-f\d]{6}$',
                                                      _("color should be a hex value!"))])
    about = models.TextField(_("about"), default="", blank=True)
    slug = models.SlugField(_("slug"), null=True, unique=True)
    following_topics = models.ManyToManyField("Topic", through="TopicFollow",
                                              related_name="people", verbose_name=_("following topics"))
    followers = models.ManyToManyField(
        'self',
        related_name='following',
        symmetrical=False,
        through='Follow',
        through_fields=('following', 'follower'),
        verbose_name=_('followers'))

    class Meta:
        indexes = [
            models.Index(fields=['slug',], name='user_slug_index'),]

    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        if not self.slug:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)

    def get_absolute_url(self, name='user'):
        return reverse(name, kwargs={"slug": self.slug})

    def ordered_followers(self):
        return self.followers.all().order_by('-following_set__pk')

    def ordered_following(self):
        return self.following.all().order_by('-followers_set__pk')

    def get_age(self):
        return (date.today().year - self.birthday.year
                if self.birthday else 0)

    def get_color(self):
        return self.color or self.DEFAULT_COLOR


class Follow(models.Model):
    following = models.ForeignKey(User,
                                  on_delete=models.CASCADE,
                                  verbose_name=_('follow to'),
                                  related_name='followers_set')
    follower = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 verbose_name=_('follower'),
                                 related_name='following_set')
    followed_date = models.DateTimeField(_('followed date'), auto_now_add=True)

    class Meta:
        ordering = ['-followed_date',]
        constraints = [
            # check that user followed once
            models.UniqueConstraint(
                fields=['following', 'follower'],
                name='follow_once',
                violation_error_message=_("Can't follow twice")),
            # check that user not following self 2
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='not_follow_self',
                violation_error_message=_("You can't follow self!"))
        ]

    def clean(self, *args, **kwargs) -> None:
        # check that user is not following self for admin
        if self.following_id == self.follower_id:
            raise ValidationError(_("Can't follow self!"))

        return super().clean(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.following.username} followed by {self.follower.username}"


class Topic(models.Model):
    DEFAULT_COLOR = "#e30066"

    image = models.ImageField(_("topic image"), upload_to="topics/%Y/%m/%d/",
                              blank=True, default="defaults/default_article.png")
    color = LowerCharField(_("color"), max_length=7, null=True, default=DEFAULT_COLOR,
                           validators=[RegexValidator(r'^#[A-fa-f\d]{6}$',
                                                      _("color should be a hex value!"))])
    title = LowerCharField(_("name"), max_length=100, unique=True)
    description = models.TextField(
        _("description"), max_length=600, default="")
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                related_name="topics")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = '-created',
        verbose_name = _("topic")
        verbose_name_plural = _("topics")
        indexes = [models.Index(
            fields=('title',), name="topic_name_index"),]

    def get_absolute_url(self, name='topic'):
        return reverse(name, kwargs={"pk": self.pk})

    def get_color(self):
        return self.color or self.DEFAULT_COLOR

    def __str__(self) -> str:
        return self.title


class TopicFollow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='following_topics_set', verbose_name=_('followed user'))
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE,
                              related_name='people_set', verbose_name=_('following topic'))
    followed_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = 'followed_date',
        constraints = models.UniqueConstraint(fields=('user', 'topic'), name='topic_follow_once',
                                              violation_error_message=_("Can't follow twice!")),

    def __str__(self) -> str:
        return f"{self.user} followed topic: {self.topic}"


def get_default_topic():
    if not Topic.objects.exists():
        Topic.objects.create(title="off topic")
    return 1


class Post(models.Model):
    image = models.ImageField(_("post image"),
                              upload_to='posts/%Y/%m/%d/',
                              default='defaults/default_article.png')
    topic = models.ForeignKey(
        Topic, on_delete=models.SET_DEFAULT, verbose_name=_("topic"), related_name='posts',
        default=get_default_topic)
    title = models.CharField(_("title"), max_length=255)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name='posts', verbose_name=_("author"))
    content = models.TextField(_("content"), max_length=10**4)

    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        ordering = '-created', '-updated'

    def get_absolute_url(self, name='post'):
        return reverse(name, kwargs={"pk": self.pk})

    @property
    def edited(self):
        return self.created != self.updated

    def __str__(self) -> str:
        return self.title[:30]


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_("post"))
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='post_comments', verbose_name=_("owner"))
    comment = models.TextField(_("comment"), max_length=10**3*2)

    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        ordering = '-created',

    def __str__(self) -> str:
        return self.comment[:50]
