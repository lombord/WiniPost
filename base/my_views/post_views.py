from django.views.generic import (View, CreateView, UpdateView,
                                  DeleteView)

from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _


from ..models import Post, Topic
from ..forms import (
    PostCreateForm, PostEditForm, PostEditForm,
    PostEditForm, PostEditForm, CommentForm,
)


from .base_views import MyBaseDetailView, MyBaseListView
from .base_mixins import MyBaseFormMixin, MySessionFormMixin


# Post view classes
class PostsView(MyBaseListView):
    model = Post
    template_name = 'base/posts/posts.html'
    context_object_name = 'posts'

    def get_lookup_args(self, query):
        return (Q(title__icontains=query) |
                Q(topic__title__icontains=query) |
                Q(author__username__icontains=query) |
                Q(content__icontains=query),)


class PostView(MyBaseDetailView):
    model = Post
    template_name = 'base/posts/post.html'
    context_object_name = 'post'

    def get_dynamic_context(self):
        comments = self.object.comments.all()
        comment_form = CommentForm()
        return {'comment_form': comment_form,
                'comments': comments}


@method_decorator(login_required(login_url='login'), name='dispatch')
class CreatePostView(MySessionFormMixin, CreateView):
    form_class = PostCreateForm
    template_name = 'base/forms/img_color_form.html'
    success_message = "Post has been added!"
    static_context = {'title': 'Add a Post',
                      'submit': 'Add', 'send_file': True}

    def get_initial(self):
        initial = super().get_initial()
        try:
            initial['topic'] = Topic.objects.get(
                pk=self.request.GET.get('topic'))
        except:
            initial['topic'] = 1
        return initial


@method_decorator(login_required(login_url='login'), name='dispatch')
class EditPostView(MyBaseFormMixin, UpdateView):
    form_class = PostEditForm
    template_name = 'base/forms/img_color_form.html'
    static_context = {'submit': 'Edit', 'send_file': True}
    success_message = "Changes have been saved!"

    def get_dynamic_context(self):
        return {'title': f"Edit {self.object.title}"}

    def get_object(self, *args, **kwargs):
        return get_object_or_404(self.request.user.posts, pk=self.kwargs.get('pk'))


@method_decorator(login_required(login_url='login'), name='dispatch')
class DeletePostView(MyBaseFormMixin, DeleteView):
    model = Post
    template_name = 'base/forms/confirm.html'
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
