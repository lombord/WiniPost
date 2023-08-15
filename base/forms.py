from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Post, User, Comment, Topic


class MyImageWidget(forms.ClearableFileInput):
    template_name = 'base/widgets/image_input.html'


class MyBaseForm():
    simple_forms = set()
    exclude_required = tuple()
    dont_show = set()
    error_css_class = 'is-invalid'
    _base_css_classes = 'form-control bg-body-tertiary'

    @property
    def base_css_classes(self):
        return self._base_css_classes

    @base_css_classes.setter
    def base_css_classes(self, new_css_classes):
        self._base_css_classes = " ".join(new_css_classes)

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
            css_classes = visible.css_classes()
            attrs['class'] = " ".join(
                (attrs.get('class', ''), self.base_css_classes, css_classes))
            if self.errors and not visible.errors:
                attrs['class'] += ' is-valid'
            attrs['placeholder'] = visible.name


class UserRelatedFormMixin():
    user_field_name = 'user'

    def __init__(self, *args, user=None, **kwargs) -> None:
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super().save(commit=False)
        setattr(obj, self.user_field_name, self.user)
        commit and obj.save()
        return obj

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


class ImgColorForm(MyBaseForm, forms.ModelForm):
    color_field_name = 'color'
    image_field_name = 'image'
    image_width = None
    image_height = None

    def get_image(self):
        return self[self.image_field_name]

    def get_color(self):
        return self.color_field_name and self[self.color_field_name]


class UserEditForm(ImgColorForm):
    exclude_required = 'email', 'about'
    dont_show = {'photo', 'color'}
    image_field_name = 'photo'

    class Meta:
        model = User
        fields = ('photo', 'color', 'first_name', 'last_name',
                  'birthday', 'email', 'about',)
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'color': forms.TextInput(attrs={'type': 'color'})
        }


# Topic forms
class TopicEditForm(ImgColorForm):
    dont_show = {'image', 'color'}
    image_width = 400
    image_height = 300

    class Meta:
        model = Topic
        exclude = 'creator', 'title'
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'})
        }


class TopicCreateForm(UserRelatedFormMixin, TopicEditForm):
    user_field_name = 'creator'

    class Meta(TopicEditForm.Meta):
        exclude = 'creator',


# Post forms
class PostEditForm(ImgColorForm):
    dont_show = {'image', }
    color_field_name = None
    image_width = 500
    image_height = 300

    class Meta:
        model = Post
        exclude = 'author', "topic"


class PostCreateForm(UserRelatedFormMixin, PostEditForm):
    user_field_name = "author"

    class Meta:
        model = Post
        exclude = 'author',


# comment forms
class CommentForm(MyBaseForm, forms.ModelForm):

    class Meta:
        model = Comment
        fields = 'comment',

    def save(self, user_pk, post_pk, commit: bool = True):
        comment = super().save(False)
        comment.owner_id = user_pk
        comment.post_id = post_pk
        if commit:
            comment.save()
        return comment
