from django import template

register = template.Library()

@register.filter
def slug_to_title(value):
    return value.replace("-", " ").title()
