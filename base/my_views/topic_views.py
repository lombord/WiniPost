from django.views.generic import (CreateView, UpdateView,)
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _


from ..models import Topic
from ..forms import (TopicEditForm, TopicCreateForm)


from .base_mixins import MySessionFormMixin, MyBaseFormMixin
from .base_views import MyBaseDetailView, MyBaseListView


# Topic view classes
class TopicsView(MyBaseListView):
    model = Topic
    template_name = 'base/topics/topics.html'
    context_object_name = 'topics'
    static_context = {'search_in': 'topics'}

    def get_queryset(self):
        return super().get_queryset().annotate(
            Count('people'),
            Count('posts')).order_by('-people__count',
                                     '-posts__count')

    def get_lookup_args(self, query):
        return (Q(title__icontains=query) |
                Q(creator__username__icontains=query) |
                Q(description__icontains=query),)


class TopicView(MyBaseDetailView):
    model = Topic
    context_object_name = 'topic'
    template_name = 'base/topics/topic.html'

    def get_dynamic_context(self):
        return {'posts': self.object.posts.all()}


@method_decorator(login_required(login_url='login'), name='dispatch')
class TopicCreateView(MySessionFormMixin, CreateView):
    form_class = TopicCreateForm
    template_name = 'base/forms/img_color_form.html'
    success_message = "Topic created successfully"
    static_context = {'title': 'Create a Topic',
                      'submit': 'Create', 'send_file': True}


@method_decorator(login_required(login_url='login'), name='dispatch')
class TopicEditView(MyBaseFormMixin, UpdateView):
    form_class = TopicEditForm
    template_name = 'base/forms/img_color_form.html'
    success_message = "Topic has been changed"
    static_context = {'submit': 'Edit', 'send_file': True}

    def get_dynamic_context(self):
        return {"title": f"Edit Topic: {self.object.title}", }

    def get_object(self, queryset=None):
        return get_object_or_404(self.request.user.topics, pk=self.kwargs.get('pk'))
