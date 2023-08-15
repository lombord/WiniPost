from functools import wraps


from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.contrib import messages


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


class MySessionFormMixin(MyBaseFormMixin):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MyBaseModelMixin(MyBaseMixin):
    values = tuple()

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if cls.values:
            cls.get_queryset = cls.set_values(cls.get_queryset)

    @staticmethod
    def set_values(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            queryset = method(self, *args, *kwargs)
            return queryset.values(*self.values)
        return wrapper
