from functools import wraps

from django.db.models import Count, F, Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import gettext as _
from django.contrib import messages

from .models import *
from .forms import (
    ArticleForm, LoginForm, UserRegisterForm, CommentForm,
    UserEditForm,
)


# Help functions and decorators
def not_authenticated(func):
    """Checks if the user is not authenticated"""
    @wraps(func)
    def wrapper(request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, _('You have already logged in!'))
            return redirect('home')
        return func(request, *args, **kwargs)

    return wrapper


def check_owner(model: type, key: str, owner_pk: str):
    """Checks if the current user owner of the object of a Model 
    wrapped view function should get obj as second positional argument

    Args:
        model (type): Model class to find an object
        key (str): name of the key to get object 
        owner_pk (str): name of the owner field in Model
    """
    def decor_func(func):

        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            obj = get_object_or_404(model, **{key: kwargs.pop(key)})
            if not request.user.is_superuser and getattr(obj, owner_pk) != request.user.pk:
                messages.warning(request, _("You aren't allowed here!"))
                return redirect(request.META.get('HTTP_REFERER', 'home'))
            return func(request, obj, *args, **kwargs)

        return wrapper

    return decor_func


# View functions
# user views
def show_users(request) -> HttpResponse:
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query))
    else:
        users = User.objects
    users = users.annotate(
        Count('followers')).order_by('-followers__count', 'username')
    context = {'users': users, 'send_to': 'users'}
    return render(request, 'base/users.html', context=context)


@not_authenticated
def register_user(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Account has been created"))
            messages.info(request, _("You are now logged as '%s'") %
                          form.cleaned_data['username'])
            return redirect('edit_profile')
        messages.error(request, _('Something went wrong!'))
    else:
        form = UserRegisterForm()
    context = {'form': form, 'title': 'Register',
               'submit': 'register'}
    return render(request, 'base/login.html', context=context)


@not_authenticated
def login_user(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    if request.method == 'POST':
        form = LoginForm(request.POST)
        form.is_valid()
        print(form.cleaned_data)
        user = authenticate(request, **form.cleaned_data)
        if user is not None:
            messages.info(request, _("You are now logged as '%s'") %
                          form.cleaned_data['username'])
            login(request, user)
            return redirect('home', permanent=True)
        messages.error(request, _('Incorrect username or password!'))
    else:
        form = LoginForm()
    context = {'form': form, 'title': 'Login',
               'submit': 'login', 'is_login': True}
    return render(request, 'base/login.html', context=context)


def show_profile(request: HttpRequest, slug: str) -> HttpResponse:
    user = get_object_or_404(User, slug=slug)
    context = {'user': user}
    return render(request, 'base/extending/user_profile.html', context=context)


def show_followers(request: HttpRequest, slug: str) -> HttpResponse:
    user = get_object_or_404(User, slug=slug)
    followers = user.followers.all()
    context = {'user': user, 'followers': followers}
    return render(request, 'base/user_followers.html', context)


def show_following(request: HttpRequest, slug: str) -> HttpResponse:
    user = get_object_or_404(User, slug=slug)
    following = user.following.all()
    context = {'user': user, 'following': following}
    return render(request, 'base/user_following.html', context)


@login_required(login_url='login')
def follow_user(request: HttpRequest, slug: str) -> HttpResponseRedirect:
    following = get_object_or_404(User, slug=slug)
    try:
        following.followers.add(request.user)
    except Exception as e:
        messages.error(request, _("U can't follow self!"))
    else:
        messages.info(request, _("You followed '%s' ") %
                      following.username)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required(login_url='login')
def unfollow_user(request: HttpRequest, slug: str) -> HttpResponseRedirect:
    following = get_object_or_404(User, slug=slug)
    try:
        following.followers.remove(request.user)
    except Exception as e:
        messages.error(request, _(str(e)))
    else:
        messages.info(request, _("You unfollowed '%s' ") %
                      following.username)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required(login_url='login')
def logout_user(request: HttpRequest) -> HttpResponseRedirect:
    messages.info(request, _("You are logged out from '%s'") %
                  request.user.username)
    logout(request)
    return redirect('home')


@login_required(login_url='login')
def edit_profile(request: HttpRequest,) -> HttpResponse | HttpResponseRedirect:
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES,
                            instance=request.user)
        if form.is_valid():
            messages.success(request, _('Changes have been saved'))
            form.save()
            return redirect('home')
        messages.error(request, _('Something went wrong'))
    else:
        form = UserEditForm(instance=request.user)
    context = {
        'form': form, 'title': f"Edit {request.user}",
        'submit': 'edit', 'send_file': True, }
    return render(request, 'base/edit_profile.html', context=context)


# post views
def show_posts(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q')
    if query:
        posts = Article.objects.filter(
            Q(title__icontains=query) |
            Q(author__username__icontains=query) |
            Q(content__icontains=query))
    else:
        posts = Article.objects.all()
    context = {'posts': posts}
    return render(request, 'base/home.html', context=context)


def show_user_posts(request: HttpRequest, slug: str) -> HttpResponse:
    user = get_object_or_404(User, slug=slug)
    posts = user.posts.all()
    context = {'posts': posts, 'user': user}
    return render(request, 'base/user_posts.html', context=context)


@login_required(login_url='login')
def add_post(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            messages.info(request, _("Post has been added!"))
            post = form.save(request.user)
            return redirect(post)
        messages.success(request, _("Something went wrong!"))
    else:
        form = ArticleForm()
    context = {'form': form, 'title': 'Add a Post',
               'submit': 'Add', 'send_file': True}
    return render(request, 'base/extending/form.html', context=context)


def show_post(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Article, pk=pk)
    comments = post.comments.all()
    comment_form = CommentForm()
    context = {'post': post, 'comment_form': comment_form,
               'comments': comments}
    return render(request, 'base/post.html', context=context)


@login_required(login_url='login')
@check_owner(Article, 'pk', 'author_id')
def edit_post(request: HttpRequest, post: Article) -> HttpResponse | HttpResponseRedirect:
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            messages.success(request, _("Changes have been saved!"))
            form.save()
            return redirect('home')
        messages.error(request, _("Something went wrong!"))
    else:
        form = ArticleForm(instance=post)
    context = {'form': form, 'title': f"Edit {post.title}",
               'submit': 'Edit', 'send_file': True}
    return render(request, 'base/extending/form.html', context)


@login_required(login_url='login')
@check_owner(Article, 'pk', 'author_id')
def delete_post(request: HttpRequest, post: Article) -> HttpResponseRedirect:
    messages.success(request, _("Post has been deleted!"))
    post.delete()
    return redirect('home')


# comment views
@login_required(login_url='login')
def post_comment(request: HttpRequest) -> HttpResponseRedirect:
    if request.method != 'POST':
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    form = CommentForm(request.POST)
    if form.is_valid():
        form.save(request.user.pk, request.POST.get('post_pk'))
    return redirect(request.META.get('HTTP_REFERER', 'home'))
