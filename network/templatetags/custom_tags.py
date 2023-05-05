from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def webpush_button():
    html = '<button class="push-notification-button" id="subscribeBtn" style="background-color: red; color: white;">Subscribe to notifications</button>'
    return mark_safe(html)