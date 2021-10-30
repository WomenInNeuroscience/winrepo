from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.contrib.messages import get_messages, constants

from profiles.models import Profile, Recommendation, User


class AccountTests(TestCase):

    def test_create(self):
        response = self.client.get(reverse('profiles:signup'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.post(reverse('profiles:signup'), data={
            'name': 'Unit Test',
            'email': 'test@test.com',
            'password1': 'myunittest1!',
            'password2': 'myunittest1!',
            'g-recaptcha-response': 'abcdef',
        })
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('username', response.context['form'].errors)

        response = self.client.post(reverse('profiles:signup'), data={
            'username': 'unittest',
            'name': 'Unit Test',
            'email': 'test@test.com',
            'password1': 'Myunitarytest1!',
            'password2': 'Myunitarytest1!',
            'g-recaptcha-response': 'abcdef',
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND, 'form' in response.context and response.context['form'].errors.as_text())
        self.assertEqual(response.url, reverse('profiles:signup_confirm'))

        u = User.objects.get(email='test@test.com')
        token = response.context['token']

        # Try tempering with the token
        response = self.client.get(reverse('profiles:signup_confirm'), data={
            'token': token + 'asdasd',
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, constants.ERROR)

        response = self.client.get(reverse('profiles:signup_confirm'), data={
            'token': token,
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('profiles:user_profile'))
        self.assertTrue('first_login' in self.client.session)

        self.client.session.flush()
        self.client.logout()

        # Not first login anymore
        u = User.objects.get(email='test@test.com')
        self.client.force_login(u)

        self.assertIsNotNone(u.last_login)
        self.assertFalse('first_login' in self.client.session)

    def test_create_different_session(self):

        response = self.client.get(reverse('profiles:signup'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.post(reverse('profiles:signup'), data={
            'username': 'unittest',
            'name': 'Unit Test',
            'email': 'test@test.com',
            'password1': 'Myunitarytest1!',
            'password2': 'Myunitarytest1!',
            'g-recaptcha-response': 'abcdef',
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND, 'form' in response.context and response.context['form'].errors.as_text())
        self.assertEqual(response.url, reverse('profiles:signup_confirm'))

        self.client.session.flush()

        u = User.objects.get(email='test@test.com')
        token = response.context['token']

        response = self.client.get(
            reverse('profiles:signup_confirm'),
            data={
                'token': token,
            }
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('profiles:login'))

    def test_account_page(self):

        u = User(email='test@test.com')
        u.is_active = True
        u.save()

        self.client.force_login(u)

        response = self.client.get(reverse('profiles:user'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'test@test.com')

    def test_account_login(self):

        u = User(email='test@test.com')
        u.is_active = True
        u.set_password('Myunitarytest1!')
        u.save()

        next = reverse('profiles:user_edit')
        response = self.client.get(reverse('profiles:login') + '?next=' + next)

        response = self.client.post(reverse('profiles:login'), {
            'username': 'test@test.com',
            'password': 'Myunitarytest1!',
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, next)

    def test_account_edit(self):

        u = User(email='test@test.com')
        u.username = 'unittest'
        u.name = 'Unit Test'
        u.is_active = True
        u.set_password('Myunitarytest1!')
        u.save()

        self.client.force_login(u)
  
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            response = self.client.post(reverse('profiles:user_edit'), {
                'username': u.username,
                'name': 'Another Unit Test',
                'email': 'different_email@test.com',
            }, follow=True)
            self.assertRedirects(response, reverse('profiles:login') + '?next=' + reverse('profiles:user'))
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(len(mail.outbox), 1)

        u.refresh_from_db()

        self.assertFalse(u.is_active)
        self.assertEqual(u.name, 'Another Unit Test')
        self.assertEqual(u.email, 'test@test.com')

        token = mail.outbox[0].context['token']

        self.assertTrue('user_confirmation_token' in self.client.session)
        self.assertEqual(self.client.session['user_confirmation_token'], token)

        response = self.client.get(reverse('profiles:signup_confirm'), data={
            'token': token,
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('profiles:user'))

    def test_delete(self):

        u = User(email='test@test.com')
        u.is_active = True
        u.save()

        p = Profile(contact_email='test@test.com', user=u)
        p.save()

        r = Recommendation(profile=p, reviewer_email='another@test.com')
        r.save()

        self.client.force_login(u)

        response = self.client.get(reverse('profiles:user_delete'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        User.objects.get(id=u.id)

        response = self.client.post(reverse('profiles:user_delete'), data={
            'confirm': True,
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('profiles:login'))

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=u.id)

        with self.assertRaises(Profile.DoesNotExist):
            Profile.objects.get(id=p.id)

        Recommendation.objects.get(id=r.id)

    def test_account_changepassword(self):

        u = User(email='test@test.com')
        u.is_active = True
        u.set_password('Myunittest1!')
        u.save()

        self.client.force_login(u)

        response = self.client.get(reverse('profiles:user_change_password'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.post(reverse('profiles:user_change_password'), data={
            'old_password': 'myuqwdnittest1!!!',
            'new_password1': 'myunittest1!passchange',
            'new_password2': 'myunittest1!passchange',
        })

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('old_password', response.context['form'].errors)

        response = self.client.post(reverse('profiles:user_change_password'), data={
            'old_password': 'Myunittest1!',
            'new_password1': 'Myunittest1!passchange',
            'new_password2': 'Myunittest1!passchange',
        })

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('profiles:user'))

