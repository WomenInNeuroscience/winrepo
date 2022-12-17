from django import template
from django.urls import reverse

register = template.Library()

@register.filter
def profile_url(profile):
    if profile.user:
        return reverse('profiles:detail_username', args=[profile.user.username])
    else:
        return reverse('profiles:detail', args=[profile.id])
