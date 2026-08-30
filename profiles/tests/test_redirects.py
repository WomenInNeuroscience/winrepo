from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse

from ..redirects import resolve_post_auth_redirect


class ResolvePostAuthRedirectTests(TestCase):
    """Unit tests for the shared post-authentication redirect helper."""

    def _future(self):
        return datetime.timestamp(datetime.now() + timedelta(minutes=15))

    def _past(self):
        return datetime.timestamp(datetime.now() - timedelta(minutes=1))

    def test_valid_next_wins(self):
        session = {'next': '/somewhere/', 'next_expiration': self._future()}
        self.assertEqual(
            resolve_post_auth_redirect(session, '/fallback/'), '/somewhere/'
        )

    def test_expired_next_is_ignored(self):
        session = {'next': '/somewhere/', 'next_expiration': self._past()}
        self.assertEqual(
            resolve_post_auth_redirect(session, '/fallback/'), '/fallback/'
        )

    def test_next_without_expiration_is_ignored(self):
        session = {'next': '/somewhere/'}
        self.assertEqual(
            resolve_post_auth_redirect(session, '/fallback/'), '/fallback/'
        )

    def test_first_login_goes_to_profile(self):
        session = {'first_login': True}
        self.assertEqual(
            resolve_post_auth_redirect(session, '/fallback/'),
            reverse('profiles:user_profile'),
        )

    def test_next_takes_priority_over_first_login(self):
        session = {
            'next': '/somewhere/',
            'next_expiration': self._future(),
            'first_login': True,
        }
        self.assertEqual(
            resolve_post_auth_redirect(session, '/fallback/'), '/somewhere/'
        )

    def test_fallback_when_nothing_set(self):
        self.assertEqual(
            resolve_post_auth_redirect({}, '/fallback/'), '/fallback/'
        )
