import random
import re
from functools import reduce
from operator import and_, or_

from dal.autocomplete import Select2QuerySetView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import logout
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.template import loader
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView, ModelFormMixin
from django.views.generic.list import ListView, View
from rest_framework import viewsets


from .forms import CreateUserForm, RecommendModelForm, UserProfileForm, UserDeleteForm
from .models import Country, Profile, Recommendation, User
from .serializers import CountrySerializer, PositionsCountSerializer


def get_user(uidb64):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(email=uid)
    except (TypeError, ValueError, OverflowError, ValidationError, AttributeError, User.DoesNotExist):
        user = None
    return user

class Home(ListView):
    template_name = 'profiles/home.html'
    context_object_name = 'recommendations_sample'
    model = Recommendation

    def get_queryset(self):
        top_reco = list(Recommendation.objects.all().order_by('-id')[:100])
        nb_samples = 6

        if len(top_reco) == 0:
            sample = []
        else:
            sample = random.sample(
                top_reco,
                nb_samples if len(top_reco) > nb_samples else len(top_reco)
            )

        return sample


class ListProfiles(ListView):
    template_name = 'profiles/list.html'
    context_object_name = 'profiles'
    model = Profile
    paginate_by = 20

    def get_queryset(self):
        s = self.request.GET.get('s')
        is_underrepresented = self.request.GET.get('ur') == 'on'
        is_senior = self.request.GET.get('senior') == 'on'

        # create filter on search terms
        # q_st = ~Q(pk=None)  # always true
        q_st = Q(is_public=True)

        if s is not None:
            # split search terms and filter empty words (if successive spaces)
            search_terms = list(filter(None, s.split(' ')))

            for st in search_terms:
                st_regex = re.compile(f'.*{st}.*', re.IGNORECASE)

                # matching_positions = list(
                #   x[0]
                #   for x in Profile.get_position_choices()
                #   if st_regex.match(x[1]))
                matching_structures = list(
                    Q(brain_structure__contains=x[0])
                    for x
                    in Profile.get_structure_choices()
                    if st_regex.match(x[1]))
                matching_modalities = list(
                    Q(modalities__contains=x[0])
                    for x
                    in Profile.get_modalities_choices()
                    if st_regex.match(x[1]))
                matching_methods = list(
                    Q(methods__contains=x[0])
                    for x
                    in Profile.get_methods_choices()
                    if st_regex.match(x[1]))
                matching_domains = list(
                    Q(domains__contains=x[0])
                    for x
                    in Profile.get_domains_choices()
                    if st_regex.match(x[1]))

                st_conditions = [
                    Q(name__icontains=st),
                    Q(institution__icontains=st),
                    Q(position__icontains=st),
                    Q(brain_structure__icontains=st),
                    Q(country__name__icontains=st),
                    Q(keywords__icontains=st),
                 ] + matching_structures \
                   + matching_modalities \
                   + matching_methods \
                   + matching_domains

                q_st = and_(reduce(or_, st_conditions), q_st)

        #  create filter on under-represented countries
        if is_underrepresented:
            q_ur = Q(country__is_under_represented=True)
        else:
            q_ur = ~Q(pk=None)  # always true

        # create filter on senior profiles
        if is_senior:
            senior_profiles_keywords = ('Senior', 'Lecturer', 'Professor',
                                        'Director', 'Principal')
            # position must contain one of the words(case insensitive)
            q_senior = reduce(or_, (Q(position__icontains=x)
                                    for x
                                    in senior_profiles_keywords))
        else:
            q_senior = ~Q(pk=None)  # always true

        # apply filters
        profiles_list = Profile.objects \
                               .filter(q_st, q_ur, q_senior) \
                               .order_by('-publish_date')

        return profiles_list


class ProfileDetail(DetailView):
    model = Profile
    queryset = Profile.objects.filter(is_public=True)


class UserProfileView(TemplateView):
    template_name = "users/user_profile.html"


class UserProfileEditView(SuccessMessageMixin, ModelFormMixin, FormView):
    template_name = "users/user_profile_form.html"
    form_class = UserProfileForm
    success_message = 'Your profile has been stored successfully!'

    def get(self, request, *args, **kwargs):
        self.object = self.request.user.profile
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.request.user.profile
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.save(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profiles:user_profile')


class UserView(LoginRequiredMixin, TemplateView):
    template_name = "users/user.html"


class UserDeleteView(LoginRequiredMixin, FormView):
    form_class = UserDeleteForm
    template_name = 'users/user_delete.html'
    success_message = 'Your account has been deleted successfully!'

    token_generator = default_token_generator

    def get(self, request, *args, **kwargs):
        uid = request.GET.get('uid')
        token = request.GET.get('token')

        user = get_user(uid)
        if token and user is not None:
            if self.token_generator.check_token(user, token):
                user.is_active = True
                if Profile.objects.filter(contact_email=user.email).exists():
                    user.profile = Profile.objects.get(contact_email=user.email)
                user.save()

            messages.success(self.request, self.success_message)
            return redirect('profiles:login')

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user

        logout(self.request)

        try:
            profile = user.profile
            profile.delete()
        except Profile.DoesNotExist:
            pass

        user.delete()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profiles:login')


class CreateUserView(CreateView):
    form_class = CreateUserForm
    template_name = 'registration/signup.html'
    subject_template_name = 'registration/signup_subject.txt'
    email_template_name = 'registration/signup_email.txt'
    html_email_template_name = 'registration/signup_email.html'

    token_generator = default_token_generator

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profiles:user_profile')
        return super().get(request, *args, **kwargs)

    def send_mail(self, user):
        context = {
            "user": user,
            "uid": urlsafe_base64_encode(force_bytes(user.email)),
            "token": self.token_generator.make_token(user)
        }
        
        subject = loader.render_to_string(self.subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(self.email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, None, [user.email])
        html_email = loader.render_to_string(self.html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def form_valid(self, form):
        self.object = form.save()
        self.send_mail(self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profiles:signup_confirm')


class CreateUserConfirmView(TemplateView):
    template_name = 'registration/signup_confirm.html'
    success_message = 'Your account has been activated successfully! Please, log-in!'

    token_generator = default_token_generator

    def get(self, request, *args, **kwargs):
        uid = request.GET.get('uid')
        token = request.GET.get('token')

        user = get_user(uid)
        if token and user is not None:
            if self.token_generator.check_token(user, token):
                user.is_active = True
                if Profile.objects.filter(contact_email=user.email).exists():
                    user.profile = Profile.objects.get(contact_email=user.email)
                user.save()

            messages.success(self.request, self.success_message)
            return redirect('profiles:login')

        return super().get(request, *args, **kwargs)


class CreateRecommendation(SuccessMessageMixin, FormView):
    template_name = 'profiles/recommendation_form.html'
    form_class = RecommendModelForm
    success_message = 'Your recommendation has been submitted successfully!'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                profile_id = self.kwargs.get('pk')
                if profile.id == profile_id:
                    return redirect('profiles:detail', pk=profile_id)
            except Profile.DoesNotExist:
                pass
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        recommendation = form.save()
        self.profile_id = recommendation.profile.id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profiles:detail', kwargs={'pk': self.profile_id})

    def get_initial(self):
        initial = super().get_initial()
        profile_id = self.kwargs.get('pk')
        if profile_id is not None:
            profile = get_object_or_404(Profile, pk=profile_id)
            initial.update({'profile': profile})
        return initial


class ProfilesAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        profiles = Profile.objects.all()

        # If search terms in request, split each word and search for them
        # in name & institution
        if self.q:
            qs = ~Q(pk=None)  # always true
            search_terms = list(filter(None, self.q.split(' ')))
            for st in search_terms:
                qs = and_(or_(Q(name__icontains=st),
                              Q(institution__icontains=st)), qs)

            profiles = profiles.filter(qs)

        return profiles


class CountriesAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        countries = Country.objects.all()

        # If search terms in request, split each word and search for them
        # in name & institution
        if self.q:
            qs = ~Q(pk=None)  # always true
            search_terms = list(filter(None, self.q.split(' ')))
            for st in search_terms:
                qs = and_(Q(name__icontains=st), qs)

            countries = countries.filter(qs)

        return countries


class RepresentedCountriesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.annotate(profiles_count=Count('profiles')) \
                              .filter(profiles_count__gt=0)
    serializer_class = CountrySerializer
    authentication_classes = []


class TopPositionsViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = []

    queryset = Profile.objects.all() \
        .values('position') \
        .annotate(profiles_count=Count('id')) \
        .order_by('-profiles_count')
    serializer_class = PositionsCountSerializer
