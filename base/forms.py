from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Article, User, Comment


class MyBaseForm():
    simple_forms = set()
    exclude_required = set()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_base_attrs()
        self.exclude_fields()

    def exclude_fields(self):
        for name in self.exclude_required:
            self.fields[name].required = False

    def set_base_attrs(self):
        for visible in self.visible_fields():
            attrs = visible.field.widget.attrs
            attrs['class'] = attrs.get('class', '') + ' form-control'
            attrs['placeholder'] = visible.name


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

    def clean_username(self):
        return self.cleaned_data['username'].lower()

class UserRegisterForm(MyBaseForm, UserCreationForm):

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + (
            'first_name', 'last_name', 'birthday')
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'})
        }


class UserEditForm(MyBaseForm, forms.ModelForm):
    simple_forms = {'photo', }
    exclude_required = {'email', 'about'}

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
