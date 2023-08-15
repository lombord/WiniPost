from django.views.generic import (
    TemplateView, RedirectView, ListView, DetailView)
from django.urls import reverse
from django.utils.translation import gettext as _


from ..models import Topic, Post, User


from .base_mixins import *


# Base Views
class MyBaseRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs) -> str | None:
        url = super().get_redirect_url(*args, **kwargs)
        if not url:
            url = self.request.META.get('HTTP_REFERER', None)
            url = url or reverse('home')
        return url


class MyBaseListView(MyBaseModelMixin, ListView):
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


class MyBaseDetailView(MyBaseModelMixin, DetailView):
    pass


# Home view
class HomeView(TemplateView):
    template_name = 'base/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.all()
        context['posts'] = Post.objects.all()
        context['users'] = User.objects.all()
        return context