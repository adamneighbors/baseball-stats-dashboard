from django import template

register = template.Library()

@register.filter(name='remove_leading_zero')
def remove_leading_zero(value):
    str_value = str(value)
    if str_value.startswith('0.'):
        return str_value[1:]
    return str_value
