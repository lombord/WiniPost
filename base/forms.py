from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Post, User, Comment


class MyImageWidget(forms.ClearableFileInput):
    template_name = 'base/widgets/image_input.html'


class MyBaseForm():
    simple_forms = set()
    exclude_required = set()
    dont_show = set()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_base_attrs()
        self.exclude_required and self.exclude_fields()

    def exclude_fields(self):
        for name in self.exclude_required:
            self.fields[name].required = False

    def set_base_attrs(self):
        for visible in self.visible_fields():
            attrs = visible.field.widget.attrs
            attrs['class'] = attrs.get('class', '') + ' form-control'
            attrs['placeholder'] = visible.name


# User forms
class LoginForm(MyBaseForm, AuthenticationForm):

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
    exclude_required = {'email', 'about'}
    dont_show = {'photo', 'color'}

    class Meta:
        model = User
        fields = ('photo', 'color', 'first_name', 'last_name',
                  'birthday', 'email', 'about',)
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'photo': MyImageWidget(attrs={'id': 'imgInput'}),
            'color': forms.TextInput(attrs={'type': 'color', 'id': 'colorInput',
                                            'class': 'color-picker py-2'})
        }


# Post forms
class PostForm(MyBaseForm, forms.ModelForm):
    simple_forms = {'image', }

    class Meta:
        model = Post
        exclude = 'author',

    def __init__(self, *args, author=None, **kwargs) -> None:
        self.author = author
        super().__init__(*args, **kwargs)

    def save(self, commit: bool = True):
        post = super().save(commit=False)
        if self.author:
            post.author_id = self.author.pk

        if commit:
            post.save()
        return post


# comment forms
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
