from http import HTTPStatus

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from ..models import User


@override_settings(RATELIMIT_ENABLE=True, LOGIN_RATELIMIT='3/m')
class LoginRateLimitTests(TestCase):
    """Login POSTs are rate-limited per IP to blunt brute-force guessing."""

    def setUp(self):
        cache.clear()  # ratelimit counters live in the cache
        self.url = reverse('profiles:login')
        self.user = User.objects.create_user(
            email='real@test.com', password='RightPass1!', username='real',
        )

    def _post(self, password):
        return self.client.post(
            self.url, {'username': 'real', 'password': password}
        )

    def test_login_succeeds_within_limit(self):
        response = self._post('RightPass1!')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_blocked_after_too_many_attempts(self):
        # Exhaust the 3/min budget with wrong passwords.
        for _ in range(3):
            self._post('wrong')
        # The next attempt is rate-limited even with the correct password.
        response = self._post('RightPass1!')
        self.assertEqual(response.status_code, HTTPStatus.OK)  # re-rendered
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_rate_limiting_can_be_disabled(self):
        with override_settings(RATELIMIT_ENABLE=False):
            for _ in range(5):
                self._post('wrong')
            # With limiting off, correct credentials still authenticate.
            response = self._post('RightPass1!')
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            self.assertIn('_auth_user_id', self.client.session)
