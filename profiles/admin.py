from django.contrib import admin
from django.apps import apps
from django.db.models import Max
from django.contrib.admin import StackedInline

from .models import (
    User, Profile, Country, Publication,
    Recommendation, RecommendationQuestion,
    RecommendationQuestionRevision, RecommendationAnswer
)
from .forms import (
    PublicationAdminForm, UserAdminForm, ProfileAdminForm,
    RecommendationQuestionRevisionForm
)


class CountryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_under_represented')

    def has_module_permission(self, request) -> bool:
        return request.user.is_superuser


class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'reviewer_name', 'reviewer_email', 'comment')
    search_fields = ('profile__name', 'reviewer_name',
                     'reviewer_email', 'comment')




from adminsortable.admin import SortableAdmin
from adminsortable.admin import NonSortableParentAdmin, SortableStackedInline


class RecommendationQuestionRevisionOrdering(StackedInline):
    model = RecommendationQuestionRevision
    extra = 0
    min_num = 1
    max_num = 1

    can_delete = False

    obj = None

    def __init__(self, *args, **kwargs):
        if 'obj' in kwargs:
            self.obj = kwargs['obj']
            del kwargs['obj']
        super().__init__(*args, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self.obj:
            qs = qs.filter(id=self.obj.last_revision.id)
        return qs


class RecommendationQuestionAdmin(SortableAdmin):
    list_display = ('_text',)
    # search_fields = ('revision', 'text', 'multiple')
    # form = RecommendationQuestionRevisionForm
    inlines = [RecommendationQuestionRevisionOrdering]

    def _text(self, obj):
        return obj.last_revision.text

    def get_inline_instances(self, request, obj):
        inline_instances = []
        for inline_class in self.inlines:
            if inline_class.model == RecommendationQuestionRevision:
                inline = inline_class(self.model, self.admin_site, obj=obj)
            else:
                inline = inline_class(self.model, self.admin_site)
            inline_instances.append(inline)
        return inline_instances


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
    search_fields = ('name', 'institution', 'email', 'is_public')
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


admin.site.site_header = 'WiNRepo Admin'

for model in apps.get_models():
    if model.__name__ and admin.site.is_registered(model):
        admin.site.unregister(model)

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Publication, PublicationAdmin)

admin.site.register(Recommendation, RecommendationAdmin)
admin.site.register(RecommendationQuestion, RecommendationQuestionAdmin)

# RecommendationQuestion
# RecommendationQuestionRevision
# RecommendationAnswer
