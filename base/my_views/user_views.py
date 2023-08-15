from django.views.generic import (CreateView, UpdateView,)
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.utils.translation import gettext as _
from django.contrib import messages


from ..models import User, Topic
from ..forms import (LoginForm,  UserRegisterForm, UserEditForm)


from .base_mixins import not_authenticated, MyBaseFormMixin
from .base_views import MyBaseListView, MyBaseDetailView, MyBaseRedirectView


# User view classes
class UsersView(MyBaseListView):
    model = User
    template_name = 'base/users/users.html'
    context_object_name = 'users'
    static_context = {'search_in': 'users'}

    def get_queryset(self):
        return super().get_queryset().annotate(
            Count('followers')).order_by('-followers__count', 'username')

    def get_lookup_args(self, query):
        return (Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query),)


@method_decorator(not_authenticated, name='dispatch')
class RegisterView(MyBaseFormMixin, CreateView):
    form_class = UserRegisterForm
    template_name = 'base/forms/login.html'
    success_url = reverse_lazy('edit_profile')

    static_context = {'title': 'Register', 'submit': 'register'}
    success_message = "Account has been created"

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def set_success_message(self, form):
        super().set_success_message(form)
        messages.info(self.request, _("You are now logged as '%s'") %
                      form.cleaned_data['username'])


@method_decorator(not_authenticated, name='dispatch')
class MyLoginView(MyBaseFormMixin, LoginView):
    template_name = 'base/forms/login.html'
    next_page = 'home'
    authentication_form = LoginForm
    static_context = {'title': 'Login', 'submit': 'login',
                      'is_login': True}

    error_message = 'Incorrect username or password!'

    def set_success_message(self, form):
        messages.info(self.request, _("You are now logged as '%s'") %
                      form.cleaned_data['username'])


@login_required(login_url='login')
def logout_user(request: HttpRequest) -> HttpResponseRedirect:
    messages.info(request, _("You are logged out from '%s'") %
                  request.user.username)
    logout(request)
    return redirect('home')


class UserProfileView(MyBaseDetailView):
    model = User
    context_object_name = 'user'
    template_name = 'base/users/user_profile.html'
    allow_empty = False


class UserPostsView(UserProfileView):
    template_name = 'base/users/user_posts.html'

    def get_dynamic_context(self):
        return {'posts': self.object.posts.all()}


class UserTopicsView(UserProfileView):
    template_name = 'base/users/user_topics.html'

    def get_dynamic_context(self):
        return {'topics': self.object.topics.all()}


class UserFollowingTopicsView(UserProfileView):
    template_name = 'base/users/user_topics.html'

    def get_dynamic_context(self):
        return {'topics': self.object.following_topics.all()}


class UserFollowersView(UserProfileView):
    template_name = 'base/users/user_followers.html'

    def get_dynamic_context(self):
        return {'followers': self.object.ordered_followers()}


class UserFollowingView(UserProfileView):
    template_name = 'base/users/user_following.html'

    def get_dynamic_context(self):
        return {'following': self.object.ordered_following()}


@method_decorator(login_required(login_url='login'), name='dispatch')
class BaseFollowSystemView(MyBaseRedirectView):
    model = None
    follow = True
    following_key = 'pk'
    followers_field = 'followers'

    def post(self, request: HttpRequest) -> HttpResponse:
        following = get_object_or_404(
            self.model, **{self.following_key: request.POST.get(self.following_key)})
        try:
            followers = getattr(following, self.followers_field)
            if self.follow:
                followers.add(request.user)
            else:
                followers.remove(request.user)
        except Exception as e:
            messages.error(request, str(e))
        else:
            messages.info(request,
                          _(f"You have {'' if self.follow else 'un'}followed %s") % following)
        return super().post(request)


@method_decorator(login_required(login_url='login'), name='dispatch')
class FollowSystemView(BaseFollowSystemView):
    model = User


@method_decorator(login_required(login_url='login'), name='dispatch')
class TopicFollowSystemView(BaseFollowSystemView):
    model = Topic
    followers_field = 'people'


@method_decorator(login_required(login_url='login'), name='dispatch')
class EditProfileView(MyBaseFormMixin, UpdateView):
    form_class = UserEditForm
    template_name = 'base/forms/img_color_form.html'
    static_context = {'submit': 'edit', 'send_file': True}
    success_message = 'Changes have been saved'

    def get_dynamic_context(self):
        return {'title': _("Edit %s") % self.object.username}

    def get_object(self, *args, **kwargs):
        return self.request.user
