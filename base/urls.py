
from django.urls import path
from django.contrib.auth.views import LoginView

from .views import *

urlpatterns = [
    path('', posts_page, name='home'),
    path('login/', login_user, name='login'),
    path('register/', register_user, name='register'),
    path('logout/', logout_user, name='logout'),
    path('user/<slug:slug>/', show_profile, name='user'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('add_post/', add_post, name='add_post'),
    path('post/<int:pk>/', show_post, name='post'),
    path('delete-post/<int:pk>/', delete_post, name='delete_post'),
    path('edit-post/<int:pk>/', edit_post, name='edit_post'),
    path('post-comment/', post_comment, name='post_comment'),
]
