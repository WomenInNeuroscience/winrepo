from django.test import TestCase, Client
from django.urls import reverse

from ..models import User, Profile, Country, Publication


class AdminTestMixin:
    """Create a superuser and log in to the admin."""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='testpass123',
        )
        self.client = Client()
        self.client.login(username='admin', password='testpass123')


class ProfileAdminTests(AdminTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.country = Country.objects.create(code='CH', name='Switzerland')
        self.profile = Profile.objects.create(
            name='Ada Lovelace',
            institution='ETH Zurich',
            contact_email='ada@example.com',
            country=self.country,
        )

    def test_changelist_loads(self):
        url = reverse('admin:profiles_profile_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_search_by_name(self):
        url = reverse('admin:profiles_profile_changelist')
        response = self.client.get(url, {'q': 'Ada'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ada Lovelace')

    def test_search_by_institution(self):
        url = reverse('admin:profiles_profile_changelist')
        response = self.client.get(url, {'q': 'ETH'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ada Lovelace')

    def test_search_by_email(self):
        url = reverse('admin:profiles_profile_changelist')
        response = self.client.get(url, {'q': 'ada@example'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ada Lovelace')

    def test_search_no_results(self):
        url = reverse('admin:profiles_profile_changelist')
        response = self.client.get(url, {'q': 'nonexistent'})
        self.assertEqual(response.status_code, 200)


class PublicationAdminTests(AdminTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.publication = Publication.objects.create(
            type='JP',
            title='Neural correlates of testing',
            authors='Lovelace, A.',
            published_at='2025-01-15',
            doi='10.1234/test',
            created_by=self.superuser,
        )

    def test_changelist_loads(self):
        url = reverse('admin:profiles_publication_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_search_by_title(self):
        url = reverse('admin:profiles_publication_changelist')
        response = self.client.get(url, {'q': 'Neural'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Neural correlates')

    def test_search_by_author(self):
        url = reverse('admin:profiles_publication_changelist')
        response = self.client.get(url, {'q': 'Lovelace'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Neural correlates')

    def test_search_by_doi(self):
        url = reverse('admin:profiles_publication_changelist')
        response = self.client.get(url, {'q': '10.1234'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Neural correlates')


class UserAdminTests(AdminTestMixin, TestCase):

    def test_changelist_loads(self):
        url = reverse('admin:profiles_user_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_search_by_username(self):
        url = reverse('admin:profiles_user_changelist')
        response = self.client.get(url, {'q': 'admin'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin')
