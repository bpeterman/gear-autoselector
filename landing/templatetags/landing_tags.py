import os

from django import template

register = template.Library()


@register.simple_tag
def get_url():
    return os.environ.get("URL")
