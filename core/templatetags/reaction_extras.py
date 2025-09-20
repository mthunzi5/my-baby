from django import template
register = template.Library()

@register.filter
def get_reaction_count(reaction_counts, args):
    msg_id, code = args.split(',')
    return reaction_counts.get((int(msg_id), code), 0)