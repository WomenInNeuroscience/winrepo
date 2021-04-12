from django.test import TestCase
from django.urls import reverse

from profiles.models import User


class SignupViewTests(TestCase):
    def test_signup(self):
        response = self.client.get(reverse('profiles:signup'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('profiles:signup'), data={
            'first_name': 'Unit',
            'last_name': 'Test',
            'email': 'test@test.com',
            'password1': 'myunittest1!',
            'password2': 'myunittest1!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profiles:signup_confirm'))
        
        u = User.objects.get(email='test@test.com')
        token = response.context['token']
        uid = response.context['uid']

        response = self.client.get(reverse('profiles:signup_confirm'), data={
            'uid': uid,
            'token': token,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profiles:login'))
