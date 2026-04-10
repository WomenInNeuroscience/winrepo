from django.test import TestCase
from django.urls import reverse

from ..models import User, Profile, Country


class SmokeTests(TestCase):
    """Verify all main pages return 200 and don't crash."""

    def setUp(self):
        self.country = Country.objects.create(code='CH', name='Switzerland')
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='Pass1234!',
        )
        self.user.is_active = True
        self.user.save()
        self.profile = Profile.objects.create(
            name='Test User',
            institution='ETH Zurich',
            position='Professor',
            country=self.country,
            user=self.user,
        )

    # -- Public pages --

    def test_home(self):
        r = self.client.get(reverse('profiles:home'))
        self.assertEqual(r.status_code, 200)

    def test_repo_list(self):
        r = self.client.get(reverse('profiles:index'))
        self.assertEqual(r.status_code, 200)

    def test_repo_search(self):
        r = self.client.get(reverse('profiles:index'), {'s': 'ETH'})
        self.assertEqual(r.status_code, 200)

    def test_repo_search_underrepresented(self):
        r = self.client.get(reverse('profiles:index'), {'ur': 'on'})
        self.assertEqual(r.status_code, 200)

    def test_repo_search_senior(self):
        r = self.client.get(reverse('profiles:index'), {'senior': 'on'})
        self.assertEqual(r.status_code, 200)

    def test_profile_detail_by_id(self):
        r = self.client.get(reverse('profiles:detail', args=[self.profile.id]))
        self.assertEqual(r.status_code, 200)

    def test_profile_detail_by_username(self):
        r = self.client.get(reverse('profiles:detail_username', args=['testuser']))
        self.assertEqual(r.status_code, 200)

    def test_faq(self):
        r = self.client.get(reverse('profiles:faq'))
        self.assertEqual(r.status_code, 200)

    def test_about(self):
        r = self.client.get(reverse('profiles:about'))
        self.assertEqual(r.status_code, 200)

    def test_publications(self):
        r = self.client.get(reverse('profiles:publications'))
        self.assertEqual(r.status_code, 200)

    def test_signup_page(self):
        r = self.client.get(reverse('profiles:signup'))
        self.assertEqual(r.status_code, 200)

    def test_login_page(self):
        r = self.client.get(reverse('profiles:login'))
        self.assertEqual(r.status_code, 200)

    # -- API endpoints --

    def test_api_profiles(self):
        r = self.client.get('/api/profiles/?format=json')
        self.assertEqual(r.status_code, 200)

    def test_api_countries(self):
        r = self.client.get('/api/countries/?format=json')
        self.assertEqual(r.status_code, 200)

    def test_api_positions(self):
        r = self.client.get('/api/positions/?format=json')
        self.assertEqual(r.status_code, 200)

    # -- Authenticated pages --

    def test_account_page_requires_login(self):
        r = self.client.get(reverse('profiles:user'))
        self.assertEqual(r.status_code, 302)  # redirects to login

    def test_account_page_logged_in(self):
        self.client.login(username='testuser', password='Pass1234!')
        r = self.client.get(reverse('profiles:user'))
        self.assertEqual(r.status_code, 200)

    def test_profile_edit_logged_in(self):
        self.client.login(username='testuser', password='Pass1234!')
        r = self.client.get(reverse('profiles:user_profile_edit'))
        self.assertEqual(r.status_code, 200)

    def test_recommend_page(self):
        r = self.client.get(reverse('profiles:recommend_profile', args=[self.profile.id]))
        self.assertEqual(r.status_code, 200)
