from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView

from rest_framework import routers

from .sitemaps import HomeSitemap, FaqSitemap, AboutSitemap, \
     ListSitemap, ProfilesSitemap
from . import views

router = routers.DefaultRouter()
router.register(r'api/countries', views.RepresentedCountriesViewSet)
router.register(r'api/positions', views.TopPositionsViewSet)


sitemaps = {
    'home': HomeSitemap,
    'list': ListSitemap,
    'faq': FaqSitemap,
    'about': AboutSitemap,
    'profiles': ProfilesSitemap,
}

app_name = 'profiles'

urlpatterns = [
    path('', views.Home.as_view(),
         name='home'),
    path('list/', views.ListProfiles.as_view(),
         name='index'),
    path('list/<int:pk>/', views.ProfileDetail.as_view(),
         name='detail'),
    path('list/<int:pk>/recommend/', views.CreateRecommendation.as_view(),
         name='recommend_profile'),
    path('list/recommend/', views.CreateRecommendation.as_view(),
         name='recommend'),

    path('faq/', TemplateView.as_view(template_name='profiles/faq.html'),
         name='faq'),
    path('about/', TemplateView.as_view(template_name='profiles/about.html'),
         name='about'),

    path('profiles-autocomplete/', views.ProfilesAutocomplete.as_view(),
         name='profiles_autocomplete'),
    path('countries-autocomplete/', views.CountriesAutocomplete.as_view(),
         name='countries_autocomplete'),

    path('profile/', views.UserProfileView.as_view(),
         name='user_profile'),
    path('profile/edit/', views.UserProfileEditView.as_view(),
         name='user_profile_edit'),

    path('signup/', views.CreateUser.as_view(),
         name='signup'),
    path('signup/confirm/', views.CreateUserConfirm.as_view(),
         name='signup_confirm'),
    path('login/', LoginView.as_view(),
         name='login'),
    path('logout/', LogoutView.as_view(),
         name='logout'),
    path('login/forgot', PasswordResetView.as_view(),
         name='login_forgot'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),

    path('', include(router.urls)),
#     path('api/', include('rest_framework.urls', namespace='rest_framework')),
]
