from django.contrib import admin
from django.apps import apps

from .models import Profile, Recommendation, Country, Publication


class CountryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_under_represented')


class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'reviewer_name', 'reviewer_email', 'comment')
    search_fields = ('profile__name', 'reviewer_name',
                     'reviewer_email', 'comment')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'institution')
    search_fields = ('name', 'institution', 'email', 'is_public')


class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'authors', 'journal_issue', 'published_at', 'doi')
    search_fields = ('title', 'authors', 'journal_issue', 'published_at', 'doi')


admin.site.site_header = 'WiNRepo Admin'

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Recommendation, RecommendationAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Publication, PublicationAdmin)
