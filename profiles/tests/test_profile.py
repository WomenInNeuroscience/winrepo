from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages, constants

from profiles.models import Profile, Recommendation, User


class ProfileTests(TestCase):

    def test_profile_delete(self):

        u = User(email='test@test.com')
        u.is_active = True
        u.save()

        p = Profile(contact_email='test@test.com', user=u)
        p.save()

        r = Recommendation(profile=p, reviewer_email='another@test.com')
        r.save()

        self.client.force_login(u)

        response = self.client.get(reverse('profiles:user_profile_delete'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        User.objects.get(id=u.id)

        response = self.client.post(reverse('profiles:user_profile_delete'), data={
            'confirm': True,
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('profiles:user'))

        p = Profile.all_objects.get(id=p.id)
        self.assertNotEquals(p.deleted_at, None)

    def test_profile_delete_new(self):

        u = User(email='test@test.com')
        u.is_active = True
        u.save()

        p = Profile(contact_email='test@test.com', user=u)
        p.save()

        self.client.force_login(u)

        response = self.client.get(reverse('profiles:user_profile_delete'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        User.objects.get(id=u.id)

        response = self.client.post(reverse('profiles:user_profile_delete'), data={
            'confirm': True,
        })
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse('profiles:user'))

        with self.assertRaises(Profile.DoesNotExist):
            p.refresh_from_db()
