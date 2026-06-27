"""Shared post-authentication redirect resolution.

The same "where do we send a just-authenticated user?" decision was duplicated
across ``LoginView``, ``UserCreateConfirmView`` and the allauth account
adapter. This centralises it so the three stay in sync.
"""
from datetime import datetime

from django.shortcuts import resolve_url


def resolve_post_auth_redirect(session, fallback):
    """Resolve where to send a just-authenticated user.

    Priority:
      1. A non-expired ``next`` URL stashed in the session (set by the login
         view after host/scheme validation).
      2. The profile page on a user's first login.
      3. ``fallback`` — the caller-specific default, returned unchanged.

    ``session`` is a request session (or any mapping); ``fallback`` is an
    already-resolved URL string.
    """
    if session.get('next') and session.get('next_expiration'):
        if datetime.timestamp(datetime.now()) < session['next_expiration']:
            return session['next']

    if session.get('first_login', False):
        return resolve_url('profiles:user_profile')

    return fallback
