from django import template

register = template.Library()


@register.simple_tag
def define(value):
    return value


@register.simple_tag
def check_owner(request, user):
    return request.user == user


@register.simple_tag
def call_method(obj, method_name, *args, **kwargs):
    return getattr(obj, method_name)(*args, **kwargs)


@register.filter
def get_url(obj, name):
    return obj.get_absolute_url(name)


@register.inclusion_tag('base/users/grid_users.html')
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


@register.inclusion_tag('base/posts/vertical_posts.html')
def render_vertical_posts(request, posts, _max=None):
    return {'request': request, 'posts': posts[:_max]}


@register.inclusion_tag('base/posts/mini_posts.html')
def render_mini_posts(posts, *, _max=None, card_width=None):
    return {'posts': posts[:_max], 'card_width': card_width}


@register.inclusion_tag('base/posts/topic_posts.html')
def render_topic_posts(posts, *, _max=None, card_width=None):
    return {'posts': posts[:_max], 'card_width': card_width}


@register.inclusion_tag('base/topics/follow_btn.html')
def topic_follow(request, topic, classes='btn-lg px-4 shadow'):
    return {'request': request, 'topic': topic, 'classes': classes}


@register.inclusion_tag('base/topics/vertical_topics.html')
def render_vertical_topics(request, topics, _max=None):
    return {'request': request, 'topics': topics.all()[:_max], }
