from http import HTTPStatus

from django.test import TestCase


class SecurityHeadersTests(TestCase):
    """The always-on security headers must be present on normal responses.

    These three don't depend on HTTPS/DEBUG, so they're asserted directly.
    HSTS and the SSL redirect are env-gated and verified at deploy time.
    """

    def test_security_headers_present_on_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')
        self.assertEqual(response.headers.get('Referrer-Policy'), 'same-origin')
