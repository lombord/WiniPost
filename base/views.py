from functools import wraps

from django.views.generic import (View, ListView, CreateView,
                                  DetailView, UpdateView, DeleteView)

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

from .models import *
from .forms import (
    PostForm, LoginForm, UserRegisterForm, CommentForm,
    UserEditForm,
)


# Help decorators
def not_authenticated(func):
    """Checks if the user is not authenticated"""
    @wraps(func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, _('You have already logged in!'))
            return redirect('home')
        return func(request, *args, **kwargs)

    return wrapper


# Base mixins and view classes
class MyBaseMixin:
    static_context = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.static_context)
        context.update(self.get_dynamic_context())
        return context

    def get_dynamic_context(self):
        return {}


class MyBaseFormMixin(MyBaseMixin):
    success_message = "Thank You!"
    error_message = "Something went wrong!"

    def form_valid(self, form) -> HttpResponse:
        self.set_success_message(form)
        return super().form_valid(form)

    def form_invalid(self, form) -> HttpResponse:
        self.set_error_message(form)
        return super().form_invalid(form)

    def set_success_message(self, form):
        messages.success(self.request, _(self.success_message))

    def set_error_message(self, form):
        messages.error(self.request, _(self.error_message))


class MyBaseListView(MyBaseMixin, ListView):
    query_key = 'q'

    def get_queryset(self):
        query = self.request.GET.get(self.query_key)
        if query:
            queryset = self.model.objects.filter(*self.get_lookup_args(query),
                                                 **self.get_lookup_kwargs(query))
        else:
            queryset = self.model.objects.all()
        return queryset

    def get_lookup_args(self, query):
        """Should return positional lookups such as Q() expressions as iterable"""
        return tuple()

    def get_lookup_kwargs(self, query):
        """Should return named lookups (e.g:field=query) as mapping"""
        return {}


# User view classes
class UsersView(MyBaseListView):
    model = User
    template_name = 'base/users.html'
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
    template_name = 'base/login.html'
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
    template_name = 'base/login.html'
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


class UserProfileView(MyBaseMixin, DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'base/extending/user_profile.html'
    allow_empty = False


class UserPostsView(UserProfileView):
    template_name = 'base/user_posts.html'

    def get_dynamic_context(self):
        return {'posts': self.object.posts.all()}


class UserFollowersView(UserProfileView):
    template_name = 'base/user_followers.html'

    def get_dynamic_context(self):
        return {'followers': self.object.ordered_followers()}


class UserFollowingView(UserProfileView):
    template_name = 'base/user_following.html'

    def get_dynamic_context(self):
        return {'following': self.object.ordered_following()}


@method_decorator(login_required(login_url='login'), name='dispatch')
class FollowSystemView(View):
    follow = True

    def get(self, request, slug: str):
        user = get_object_or_404(User, slug=slug)
        try:
            if self.follow:
                user.followers.add(request.user)
            else:
                user.followers.remove(request.user)
        except Exception as e:
            print(e)
            messages.error(request, _("Something went wrong!"))
        else:
            messages.info(request, _(f"You {(not self.follow or '') and 'un'}followed '%s' ") %
                          user.username)
        return redirect(request.META.get('HTTP_REFERER', 'home'))


@method_decorator(login_required(login_url='login'), name='dispatch')
class EditProfileView(MyBaseFormMixin, UpdateView):
    form_class = UserEditForm
    template_name = 'base/edit_profile.html'
    static_context = {'submit': 'edit', 'send_file': True}
    success_message = 'Changes have been saved'

    def get_dynamic_context(self):
        return {'title': _("Edit %s") % self.object.username}

    def get_object(self, *args, **kwargs):
        return self.request.user


# Post view classes
class PostsView(MyBaseListView):
    model = Post
    template_name = 'base/home.html'
    context_object_name = 'posts'

    def get_lookup_args(self, query):
        return (Q(title__icontains=query) |
                Q(author__username__icontains=query) |
                Q(content__icontains=query),)


class PostView(MyBaseMixin, DetailView):
    model = Post
    template_name = 'base/post.html'
    context_object_name = 'post'

    def get_dynamic_context(self):
        comments = self.object.comments.all()
        comment_form = CommentForm()
        return {'comment_form': comment_form,
                'comments': comments}


@method_decorator(login_required(login_url='login'), name='dispatch')
class CreatePostView(MyBaseFormMixin, CreateView):
    form_class = PostForm
    template_name = 'base/extending/form.html'
    success_message = "Post has been added!"
    static_context = {'title': 'Add a Post',
                      'submit': 'Add', 'send_file': True}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['author'] = self.request.user
        return kwargs


@method_decorator(login_required(login_url='login'), name='dispatch')
class EditPostView(MyBaseFormMixin, UpdateView):
    form_class = PostForm
    template_name = 'base/extending/form.html'
    static_context = {'submit': 'Edit', 'send_file': True}
    success_message = "Changes have been saved!"

    def get_dynamic_context(self):
        return {'title': f"Edit {self.object.title}"}

    def get_object(self, *args, **kwargs):
        return get_object_or_404(self.request.user.posts, pk=self.kwargs.get('pk'))


@method_decorator(login_required(login_url='login'), name='dispatch')
class DeletePostView(MyBaseFormMixin, DeleteView):
    model = Post
    template_name = 'base/confirm.html'
    success_url = reverse_lazy('home')
    success_message = "Post has been deleted!"

    def get_object(self, *args, **kwargs):
        return get_object_or_404(self.request.user.posts, pk=self.kwargs.get('pk'))


@method_decorator(login_required(login_url='login'), name='dispatch')
class PostCommentView(View):
    form_class = CommentForm

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        super().dispatch(request, *args, **kwargs)
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    def post(self, request: HttpRequest, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(request.user.pk, request.POST.get('post_pk'))
