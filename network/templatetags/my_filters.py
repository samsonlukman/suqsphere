from django import template

register = template.Library()

@register.filter
def split_paragraphs(value):
    return value.split('\n')