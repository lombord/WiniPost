from django import template

register = template.Library()


@register.simple_tag
def check_owner(request, user):
    return request.user == user


@register.simple_tag
def call_method(obj, method_name, *args, **kwargs):
    return getattr(obj, method_name)(*args, **kwargs)


@register.filter
def get_url(obj, name):
    return obj.get_absolute_url(name)


@register.inclusion_tag('base/including/render_users.html')
def render_users(request, users, is_users=False, _max=None):
    user_in = False
    if not is_users:
        user_in = request.user in users
        if _max is not None and user_in:
            _max -= 1

    return {'request': request,
            'user_in': user_in,
            'is_users': is_users,
            'users': users.exclude(pk=request.user.pk)[:_max]}


@register.inclusion_tag('base/including/render_mini_posts.html')
def render_mini_posts(posts, _max=None):
    return {'posts': posts[:_max]}
