
from django.urls import path
from django.contrib.auth.views import LoginView

from .views import *

urlpatterns = [
    path('', show_posts, name='home'),
    # user urls
    path('users/', show_users, name='users'),
    path('login/', login_user, name='login'),
    path('register/', register_user, name='register'),
    path('logout/', logout_user, name='logout'),
    path('user/<slug:slug>/', show_profile, name='user'),
    path('user/<slug:slug>/posts/', show_user_posts, name='user_posts'),
    path('user/<slug:slug>/followers/', show_followers, name='followers'),
    path('user/<slug:slug>/following/', show_following, name='following'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('follow/<slug:slug>/', follow_user, name='follow'),
    path('unfollow/<slug:slug>/', unfollow_user, name='unfollow'),

    # post urls
    path('add_post/', add_post, name='add_post'),
    path('post/<int:pk>/', show_post, name='post'),
    path('delete-post/<int:pk>/', delete_post, name='delete_post'),
    path('edit-post/<int:pk>/', edit_post, name='edit_post'),

    # comment urls
    path('post-comment/', post_comment, name='post_comment'),
]
