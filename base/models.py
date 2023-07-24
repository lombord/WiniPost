from datetime import date

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.urls import reverse


class User(AbstractUser):
    photo = models.ImageField(
        upload_to="users/photos/%Y/%m/%d/", default="defaults/default-user.png")
    birthday = models.DateField(null=True, validators=[
                                MaxValueValidator(date.today,
                                                  _('Please choose correct birthday!')),])
    about = models.TextField(default="")
    slug = models.SlugField(null=True, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['slug',]),]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)

    def get_absolute_url(self, name='user'):
        return reverse(name, kwargs={"slug": self.slug})


class Article(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to='articles/%Y/%m/%d/', default='defaults/default_article.png')
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    content = models.TextField(max_length=10**4)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = '-updated', '-created'

    def get_absolute_url(self, name='post'):
        return reverse(name, kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return f"{self.author}:{self.title}"


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=10**3*2)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = '-created',

    def __str__(self) -> str:
        return self.comment[:50]
