from django.contrib import admin

# Register your models here.
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
    list_display = ('title', 'authors', 'journal_issue', 'date', 'doi')
    search_fields = ('title', 'authors', 'journal_issue', 'date', 'doi')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Recommendation, RecommendationAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Publication, PublicationAdmin)
