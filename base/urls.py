
from django.urls import path

from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    # user urls
    path('users/', UsersView.as_view(), name='users'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', logout_user, name='logout'),
    path('user/<slug:slug>/', UserProfileView.as_view(), name='user'),
    path('user/<slug:slug>/posts/', UserPostsView.as_view(), name='user_posts'),
    path('user/<slug:slug>/topics/', UserTopicsView.as_view(), name='user_topics'),
    path('user/<slug:slug>/following-topics/',
         UserFollowingTopicsView.as_view(), name='user_following_topics'),
    path('user/<slug:slug>/followers/',
         UserFollowersView.as_view(), name='followers'),
    path('user/<slug:slug>/following/',
         UserFollowingView.as_view(), name='following'),
    path('edit-profile/', EditProfileView.as_view(), name='edit_profile'),
    path('follow/', FollowSystemView.as_view(), name='follow'),
    path('unfollow/',
         FollowSystemView.as_view(follow=False), name='unfollow'),

    # topic urls
    path('topics/', TopicsView.as_view(), name='topics'),
    path('topic/<int:pk>/', TopicView.as_view(), name='topic'),
    path('create-topic/', TopicCreateView.as_view(), name='create_topic'),
    path('edit-topic/<int:pk>/', TopicEditView.as_view(), name='edit_topic'),
    path('follow-topic/', TopicFollowSystemView.as_view(), name='follow_topic'),
    path('unfollow-topic/',
         TopicFollowSystemView.as_view(follow=False), name='unfollow_topic'),

    # post urls
    path('posts/', PostsView.as_view(), name='posts'),
    path('add_post/', CreatePostView.as_view(), name='add_post'),
    path('post/<int:pk>/', PostView.as_view(), name='post'),
    path('edit-post/<int:pk>/', EditPostView.as_view(), name='edit_post'),
    path('delete-post/<int:pk>/', DeletePostView.as_view(), name='delete_post'),

    # comment urls
    path('post-comment/', PostCommentView.as_view(), name='post_comment'),

    # other urls
    path("create-menu/", CreateMenuView.as_view(), name='create_menu'),
]
