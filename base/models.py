from datetime import date

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.urls import reverse


class User(AbstractUser):
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    photo = models.ImageField(
        upload_to="users/photos/%Y/%m/%d/", default="defaults/default-user.png")
    birthday = models.DateField(_("birthday"), null=True, validators=[
                                MaxValueValidator(date.today,
                                                  _('Please choose correct birthday!')),])
    about = models.TextField(_("about"), default="")
    slug = models.SlugField(_("slug"), null=True, unique=True)
    followers = models.ManyToManyField(
        'self',
        related_name='following',
        symmetrical=False,
        through='Follow',
        through_fields=('following', 'follower'))

    class Meta:
        indexes = [
            models.Index(fields=['slug',]),]

    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        if not self.slug:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)

    def get_absolute_url(self, name='user'):
        return reverse(name, kwargs={"slug": self.slug})

    def get_age(self):
        return (date.today().year - self.birthday.year
                if self.birthday else 0)


class Follow(models.Model):
    following = models.ForeignKey(User,
                                  on_delete=models.CASCADE,
                                  verbose_name=_('follow to'),
                                  related_name='followers_set')
    follower = models.ForeignKey(User,
                                 on_delete=models.CASCADE,
                                 verbose_name=_('follower'),
                                 related_name='followed_set')
    followed_time = models.DateTimeField(auto_now_add=True)

    class Meta:
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


class Article(models.Model):
    title = models.CharField(_("title"), max_length=255)
    image = models.ImageField(_("post image"),
                              upload_to='articles/%Y/%m/%d/', 
                              default='defaults/default_article.png')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name='posts', verbose_name=_("author"))
    content = models.TextField(_("content"), max_length=10**4)

    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    class Meta:
        ordering = '-updated', '-created'

    def get_absolute_url(self, name='post'):
        return reverse(name, kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return f"{self.author}:{self.title}"


class Comment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='comments', verbose_name=_("article"))
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='post_comments', verbose_name=_("owner"))
    comment = models.TextField(_("comment"), max_length=10**3*2)
    created = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        ordering = '-created',

    def __str__(self) -> str:
        return self.comment[:50]
