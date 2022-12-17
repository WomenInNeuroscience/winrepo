from django.contrib import admin
from django.apps import apps

from .models import User, Profile, Recommendation, Country, Publication, Event
from .forms import PublicationAdminForm, UserAdminForm, ProfileAdminForm, EventAdminForm


class CountryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_under_represented')

    def has_module_permission(self, request) -> bool:
        return request.user.is_superuser


class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'reviewer_name', 'reviewer_email', 'comment')
    search_fields = ('profile__name', 'reviewer_name',
                     'reviewer_email', 'comment')


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'email', '_has_profile')
    search_fields = ('username', 'name', 'email')
    form = UserAdminForm

    def has_module_permission(self, request) -> bool:
        return request.user.is_superuser

    def _has_profile(self, obj):
        return obj.profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'institution', 'published_at')
    search_fields = ('name', 'institution', 'is_public')
    form = ProfileAdminForm


class PublicationAdmin(admin.ModelAdmin):
    list_display = ('type', 'title', 'authors', 'published_at', 'doi', '_created_by')
    search_fields = ('type', 'title', 'authors', 'published_at', 'doi', '_created_by')
    form = PublicationAdminForm

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff

    def has_module_permission(self, request):
        return request.user.is_staff

    def _created_by(self, obj):
        return obj.created_by.name

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial['created_by'] = request.user
        return initial

class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff

    def has_module_permission(self, request):
        return request.user.is_staff


admin.site.site_header = 'WiNRepo Admin'

for model in apps.get_models():
    if model.__name__ and admin.site.is_registered(model):
        admin.site.unregister(model)

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Recommendation, RecommendationAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Event, EventAdmin)
