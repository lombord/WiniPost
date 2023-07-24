from django import template

register = template.Library()


@register.simple_tag
def call_method(obj, method_name, *args, **kwargs):
    return getattr(obj, method_name)(*args, **kwargs)


@register.filter
def get_url(obj, name):
    return obj.get_absolute_url(name)
