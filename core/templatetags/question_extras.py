from django import template

register = template.Library()

@register.filter
def get_option(question, opt):
    # Assumes your Question model has fields: option_a, option_b, option_c, option_d
    return getattr(question, f'option_{opt.lower()}', '')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)