from django.contrib import sitemaps
from django.urls import reverse

from .models import Profile


class HomeSitemap(sitemaps.Sitemap):
    priority = 0.4
    changefreq = 'monthly'

    def items(self):
        return ['profiles:home']

    def location(self, item):
        return reverse(item)


class FaqSitemap(sitemaps.Sitemap):
    priority = 0.4
    changefreq = 'yearly'

    def items(self):
        return ['profiles:faq']

    def location(self, item):
        return reverse(item)


class AboutSitemap(sitemaps.Sitemap):
    # The former "About" page is now the "People" page (under the About menu).
    # We keep the class name so existing imports/registrations stay valid, but
    # point it at the canonical 'profiles:people' URL instead of the old
    # 'profiles:about' (which now only 301-redirects to People).
    priority = 0.5
    changefreq = 'yearly'

    def items(self):
        return ['profiles:people']

    def location(self, item):
        return reverse(item)


class SponsorsSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'yearly'

    def items(self):
        return ['profiles:sponsors']

    def location(self, item):
        return reverse(item)


class ListSitemap(sitemaps.Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return ['profiles:index']

    def location(self, item):
        return reverse(item)


class ProfilesSitemap(sitemaps.Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Profile.objects.filter(is_public=True)

    def lastmod(self, obj):
        return obj.updated_at