from datetime import datetime
from allauth.utils import email_address_exists
from django.conf import settings
from django.shortcuts import redirect, resolve_url
from django.contrib import messages
from allauth.account.adapter import DefaultAccountAdapter, get_adapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from .models import User


class AccountAdapter(DefaultAccountAdapter):

    def add_message(
        self,
        request,
        level,
        message_template,
        message_context=None,
        extra_tags="",
    ):
        if level == messages.SUCCESS:  # Hack to hide logged-in message
            return
        
        super().add_message(request, level, message_template, message_context, extra_tags)

    def save_user(self, request, user, form, commit=True):
        if commit:
            user.save()
        return user

    def get_login_redirect_url(self, request):
        assert request.user.is_authenticated

        # TODO deduplicate code with views.py
        if request.session.get('next') and \
            request.session.get('next_expiration'):

            if datetime.timestamp(datetime.now()) < request.session['next_expiration']:
                return request.session.get('next')

        url = settings.LOGIN_REDIRECT_URL
        return resolve_url(url)


class SocialAccountAdapter(DefaultSocialAccountAdapter):

    duplicated_email_error_message = "A user with this email already exists. Please sign-in or recover your password."

    def pre_social_login(self, request, sociallogin):
        if not sociallogin.is_existing and sociallogin.user.email:
            if email_address_exists(sociallogin.user.email):
                messages.error(request, self.duplicated_email_error_message)
                raise ImmediateHttpResponse(redirect(settings.LOGIN_REDIRECT_URL))

    def populate_user(self, request, sociallogin, data):
        username = data.get("username")
        first_name = data.get("first_name") or ""
        last_name = data.get("last_name") or ""
        email = data.get("email") or ""
        name = data.get("name") or ""
        user = sociallogin.user
        if sociallogin.account.provider == "google":
            user.username = email.partition("@")[0]
        else:
            user.username = username
        user.name = (first_name.strip() + " " + last_name.strip()).strip() or name
        user.email = email
        user.is_active = True
        user.password = None
        return user

    def save_user(self, request, sociallogin, form=None):
        u = sociallogin.user
        get_adapter().populate_username(request, u)
        sociallogin.save(request)
        return u
