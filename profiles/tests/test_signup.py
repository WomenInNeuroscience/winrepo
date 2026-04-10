from http import HTTPStatus
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from ..models import User


class SignupEmailFailureTests(TestCase):
    """Verify signup doesn't crash when email sending fails (issue #47)."""

    def _signup_data(self):
        return {
            'username': 'newuser',
            'name': 'New User',
            'email': 'new@test.com',
            'password1': 'Myunitarytest1!',
            'password2': 'Myunitarytest1!',
            'g-recaptcha-response': 'abcdef',
        }

    def test_signup_sends_email(self):
        """Normal signup sends a confirmation email."""
        response = self.client.post(reverse('profiles:signup'), data=self._signup_data())
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(User.objects.filter(email='new@test.com').exists())

    @patch('profiles.views.user_create_confirm_email')
    def test_signup_survives_email_failure(self, mock_email):
        """Signup completes even when email sending raises an exception."""
        mock_email.return_value.send.side_effect = Exception('SMTP connection refused')

        response = self.client.post(reverse('profiles:signup'), data=self._signup_data())
        # Should redirect to confirm page, not 500
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('profiles:signup_confirm'))
        # User should still be created
        self.assertTrue(User.objects.filter(email='new@test.com').exists())
