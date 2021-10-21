from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter, get_adapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class AccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        if commit:
            user.save()
        return user


class SocialAccountAdapter(DefaultSocialAccountAdapter):

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
