from django.test import TestCase
from django.urls import reverse

from ..models import User, Profile, Country, Recommendation


class ProfileSearchAPITests(TestCase):

    def setUp(self):
        self.ch = Country.objects.create(
            code='CH', name='Switzerland', is_under_represented=False,
        )
        self.ng = Country.objects.create(
            code='NG', name='Nigeria', is_under_represented=True,
        )
        self.user = User.objects.create_user(
            username='ada', email='ada@test.com', password='test',
        )
        self.profile_ch = Profile.objects.create(
            name='Ada Lovelace',
            institution='ETH Zurich',
            position='Professor',
            country=self.ch,
            keywords='attention EEG',
            modalities='EP,MR',
            domains='AT,MM',
            user=self.user,
        )
        self.profile_ng = Profile.objects.create(
            name='Ngozi Okafor',
            institution='University of Lagos',
            position='PhD student',
            country=self.ng,
            keywords='sleep fNIRS',
            modalities='FN',
            domains='SL',
        )
        # private profile — should not appear
        Profile.objects.create(
            name='Hidden Profile',
            institution='Secret Lab',
            is_public=False,
            country=self.ch,
        )

    def test_api_returns_public_profiles_only(self):
        url = '/api/profiles/?format=json'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        names = [p['name'] for p in response.json()]
        self.assertIn('Ada Lovelace', names)
        self.assertIn('Ngozi Okafor', names)
        self.assertNotIn('Hidden Profile', names)

    def test_api_contains_expected_fields(self):
        url = '/api/profiles/?format=json'
        response = self.client.get(url)
        profile = next(p for p in response.json() if p['name'] == 'Ada Lovelace')
        self.assertEqual(profile['institution'], 'ETH Zurich')
        self.assertEqual(profile['position'], 'Professor')
        self.assertEqual(profile['country_name'], 'Switzerland')
        self.assertFalse(profile['country_is_under_represented'])
        self.assertEqual(profile['username'], 'ada')
        self.assertIn('Electrophysiology', profile['modalities_display'])
        self.assertIn('Attention', profile['domains_display'])
        self.assertEqual(profile['keywords'], 'attention EEG')

    def test_api_no_pagination(self):
        """All profiles returned in a single response (no pagination)."""
        url = '/api/profiles/?format=json'
        response = self.client.get(url)
        # response is a list, not a paginated dict
        self.assertIsInstance(response.json(), list)

    def test_api_includes_recommendation_count(self):
        Recommendation.objects.create(
            profile=self.profile_ch,
            reviewer_name='Reviewer',
            reviewer_institution='MIT',
            comment='Great work',
        )
        Recommendation.objects.create(
            profile=self.profile_ch,
            reviewer_name='Reviewer 2',
            reviewer_institution='Oxford',
            comment='Excellent',
        )
        url = '/api/profiles/?format=json'
        response = self.client.get(url)
        profile = next(p for p in response.json() if p['name'] == 'Ada Lovelace')
        self.assertEqual(profile['recommendation_count'], 2)

    def test_under_represented_flag(self):
        url = '/api/profiles/?format=json'
        response = self.client.get(url)
        ng_profile = next(p for p in response.json() if p['name'] == 'Ngozi Okafor')
        self.assertTrue(ng_profile['country_is_under_represented'])
