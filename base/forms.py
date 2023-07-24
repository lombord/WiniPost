from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Article, User, Comment


class MyBaseForm():
    simple_forms = set()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs.update(
                {'class': 'form-control',
                 'placeholder': visible.name})


class ArticleForm(MyBaseForm, forms.ModelForm):
    simple_forms = {'image', }

    class Meta:
        model = Article
        exclude = 'author',

    def save(self, author=None, commit: bool = True):
        post = super().save(commit=False)
        if author is not None:
            post.author_id = author.id
        if commit:
            post.save()
        return post


class LoginForm(MyBaseForm, forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(max_length=255, widget=forms.PasswordInput())


class UserRegisterForm(MyBaseForm, UserCreationForm):

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields


class UserEditForm(MyBaseForm, forms.ModelForm):
    simple_forms = {'photo', }

    class Meta:
        model = User
        fields = ('photo', 'first_name', 'last_name',
                  'birthday', 'email', 'about')
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'photo': forms.ClearableFileInput(attrs={'id': 'img_input'})
        }


class CommentForm(MyBaseForm, forms.ModelForm):

    class Meta:
        model = Comment
        fields = 'comment',

    def save(self, user_pk, article_pk, commit: bool = True):
        comment = super().save(False)
        comment.owner_id = user_pk
        comment.article_id = article_pk
        if commit:
            comment.save()
        return comment
