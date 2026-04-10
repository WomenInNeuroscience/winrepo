from django.test import TestCase

from ..forms import UserProfileForm
from ..models import Country


class UserProfileFormCleanTests(TestCase):
    """Verify that clean() properly normalises social media URLs."""

    def setUp(self):
        self.country = Country.objects.create(code='CH', name='Switzerland')
        self.base_data = {
            'name': 'Test User',
            'institution': 'ETH Zurich',
            'country': self.country.pk,
            'orcid': '',
            'twitter': '',
            'linkedin': '',
            'github': '',
            'google_scholar': '',
            'researchgate': '',
            'position': '',
            'grad_month': '',
            'grad_year': '',
            'brain_structure': [],
            'modalities': [],
            'methods': [],
            'domains': [],
            'keywords': '',
            'contact_email': '',
            'webpage': '',
        }

    def test_orcid_url_normalised(self):
        data = {**self.base_data, 'orcid': 'https://orcid.org/0000-0001-2345-6789'}
        f = UserProfileForm(data)
        self.assertTrue(f.is_valid(), f.errors)
        self.assertEqual(f.cleaned_data['orcid'], '0000-0001-2345-6789')

    def test_orcid_raw_id_accepted(self):
        data = {**self.base_data, 'orcid': '0000-0001-2345-6789'}
        f = UserProfileForm(data)
        self.assertTrue(f.is_valid(), f.errors)
        self.assertEqual(f.cleaned_data['orcid'], '0000-0001-2345-6789')

    def test_twitter_url_normalised(self):
        data = {**self.base_data, 'twitter': 'https://twitter.com/testuser'}
        f = UserProfileForm(data)
        self.assertTrue(f.is_valid(), f.errors)
        self.assertEqual(f.cleaned_data['twitter'], 'testuser')

    def test_twitter_handle_normalised(self):
        data = {**self.base_data, 'twitter': '@testuser'}
        f = UserProfileForm(data)
        self.assertTrue(f.is_valid(), f.errors)
        self.assertEqual(f.cleaned_data['twitter'], 'testuser')

    def test_github_url_normalised(self):
        data = {**self.base_data, 'github': 'https://github.com/octocat'}
        f = UserProfileForm(data)
        self.assertTrue(f.is_valid(), f.errors)
        self.assertEqual(f.cleaned_data['github'], 'octocat')

    def test_linkedin_url_normalised(self):
        data = {**self.base_data, 'linkedin': 'https://linkedin.com/in/janesmith'}
        f = UserProfileForm(data)
        self.assertTrue(f.is_valid(), f.errors)
        self.assertEqual(f.cleaned_data['linkedin'], 'janesmith')

    def test_invalid_orcid_rejected(self):
        data = {**self.base_data, 'orcid': 'not-a-valid-orcid'}
        f = UserProfileForm(data)
        self.assertFalse(f.is_valid())
        self.assertIn('orcid', f.errors)
