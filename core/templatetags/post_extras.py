from django import template

register = template.Library()

@register.filter
def has_liked(post, user):
    """
    Usage in template: {% if post|has_liked:user %}
    Returns True if the user has reacted/liked the post.
    """
    # Defensive: check if post has a 'reactions' related manager
    reactions = getattr(post, 'reactions', None)
    if reactions and hasattr(reactions, 'filter'):
        return reactions.filter(user=user).exists()
    return False