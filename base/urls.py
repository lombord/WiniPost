
from django.urls import path

from .views import *

urlpatterns = [
    path('', PostsView.as_view(), name='home'),
    # user urls
    path('users/', UsersView.as_view(), name='users'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', logout_user, name='logout'),
    path('user/<slug:slug>/', UserProfileView.as_view(), name='user'),
    path('user/<slug:slug>/posts/', UserPostsView.as_view(), name='user_posts'),
    path('user/<slug:slug>/followers/',
         UserFollowersView.as_view(), name='followers'),
    path('user/<slug:slug>/following/',
         UserFollowingView.as_view(), name='following'),
    path('edit-profile/', EditProfileView.as_view(), name='edit_profile'),
    path('follow/<slug:slug>/', FollowSystemView.as_view(), name='follow'),
    path('unfollow/<slug:slug>/',
         FollowSystemView.as_view(follow=False), name='unfollow'),

    # post urls
    path('add_post/', CreatePostView.as_view(), name='add_post'),
    path('post/<int:pk>/', PostView.as_view(), name='post'),
    path('edit-post/<int:pk>/', EditPostView.as_view(), name='edit_post'),
    path('delete-post/<int:pk>/', DeletePostView.as_view(), name='delete_post'),

    # comment urls
    path('post-comment/', PostCommentView.as_view(), name='post_comment'),
]
