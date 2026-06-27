from http import HTTPStatus
from unittest.mock import patch

from django.core import mail
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
        """Normal signup dispatches a confirmation email to the new address.

        Backend-agnostic: asserts the message actually reaches the outbox, so
        the SendGrid->Brevo backend swap is provably non-breaking.
        """
        response = self.client.post(reverse('profiles:signup'), data=self._signup_data())
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(User.objects.filter(email='new@test.com').exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('new@test.com', mail.outbox[0].to)

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


class SignupHoneypotTests(TestCase):
    """Verify the honeypot field blocks bot submissions."""

    def _signup_data(self, **overrides):
        data = {
            'username': 'botuser',
            'name': 'Bot User',
            'email': 'bot@test.com',
            'password1': 'Myunitarytest1!',
            'password2': 'Myunitarytest1!',
            'g-recaptcha-response': 'abcdef',
        }
        data.update(overrides)
        return data

    def test_signup_rejects_filled_honeypot(self):
        """Submissions with the honeypot field filled are rejected."""
        response = self.client.post(
            reverse('profiles:signup'),
            data=self._signup_data(website='https://spam.example.com'),
        )
        # Form is invalid, page re-renders (200), no user created.
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(User.objects.filter(email='bot@test.com').exists())

    def test_signup_accepts_empty_honeypot(self):
        """Humans who leave the honeypot empty are allowed through."""
        response = self.client.post(
            reverse('profiles:signup'),
            data=self._signup_data(website=''),
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(User.objects.filter(email='bot@test.com').exists())


class SignupDisposableEmailTests(TestCase):
    """Verify signups from known disposable email providers are rejected."""

    def _signup_data(self, email):
        return {
            'username': 'spammer',
            'name': 'Spammer',
            'email': email,
            'password1': 'Myunitarytest1!',
            'password2': 'Myunitarytest1!',
            'g-recaptcha-response': 'abcdef',
        }

    def test_rejects_known_disposable_domain(self):
        response = self.client.post(
            reverse('profiles:signup'),
            data=self._signup_data('test@minitts.net'),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(User.objects.filter(email='test@minitts.net').exists())

    def test_rejects_triol_site(self):
        response = self.client.post(
            reverse('profiles:signup'),
            data=self._signup_data('hello@triol.site'),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(User.objects.filter(email='hello@triol.site').exists())

    def test_allows_legitimate_domain(self):
        response = self.client.post(
            reverse('profiles:signup'),
            data=self._signup_data('real@stanford.edu'),
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(User.objects.filter(email='real@stanford.edu').exists())
