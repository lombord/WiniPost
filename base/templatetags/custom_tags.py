from django import template

register = template.Library()


@register.simple_tag
def check_owner(request, user):
    return request.user.pk == user.pk


@register.simple_tag
def call_method(obj, method_name, *args, **kwargs):
    return getattr(obj, method_name)(*args, **kwargs)


@register.filter
def get_url(obj, name):
    return obj.get_absolute_url(name)


@register.inclusion_tag('base/render_users.html')
def render_users(request, users, _max=None):
    user_in = request.user in users
    return {'request': request,
            'user_in': user_in,
            'users': users.exclude(pk=request.user.pk)[:_max]}
