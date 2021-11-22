from django import template

from catalogue.models import Category

register = template.Library()


@register.simple_tag
def get_parent_category():
    return Category.objects.filter(parent=None)


@register.simple_tag
def get_child_category(parent):
    return Category.objects.filter(parent=parent)
