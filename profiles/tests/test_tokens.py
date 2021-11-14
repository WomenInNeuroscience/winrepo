import datetime
from django.test import TestCase
from unittest.mock import Mock, patch
from profiles.tokens import UserCreateToken
from profiles.models import User


class ProfileTests(TestCase):

    def test_user_create_token(self):

        user = User.objects.create_user(
            username='test',
            name='Test',
            email='test@winrepo.org',
            password='test',
        )
        user.save()

        token = UserCreateToken.generate(user)
        self.assertTrue(UserCreateToken.check(token))


    def test_user_create_token_expiration(self):

        user = User.objects.create_user(
            username='test',
            name='Test',
            email='test@winrepo.org',
            password='test',
        )
        user.save()

        datetime_mock = Mock(wraps=datetime.datetime)
        datetime_mock.now.return_value = datetime.datetime.now() - datetime.timedelta(minutes=30)
        with patch('datetime.datetime', new=datetime_mock):
            token = UserCreateToken.generate(user)
            self.assertFalse(UserCreateToken.check(token))
