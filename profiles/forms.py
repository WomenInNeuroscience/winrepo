from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from dal.autocomplete import ModelSelect2
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import Profile, Recommendation, User


class CaptchaForm(forms.Form):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox, label=False)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username',
            'name',
            'email',
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'name',
            'institution',
            'country',
            'contact_email',
            'webpage',
            'position',
            'grad_month',
            'grad_year',
            'brain_structure',
            'modalities',
            'methods',
            'domains',
            'keywords',
        )

    def save(self, user=None):
        user_profile = super(UserProfileForm, self).save(commit=False)
        if user:
            user_profile.user = user
        user_profile.save()
        return user_profile


class UserProfileDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        widget=forms.HiddenInput(),
        required=True,
        initial=True
    )


class UserDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        widget=forms.HiddenInput(),
        required=True,
        initial=True
    )


class UserCreateForm(CaptchaForm, UserCreationForm):
    username = forms.SlugField(required=True)
    email = forms.EmailField(required=True)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False

        if commit:
            user.save()

        return user

    class Meta:
        model = User
        fields = ('username', 'name', 'email',)
        labels = {
            'username': _('User Name'),
            'email': _('Email Address'),
        }
        help_texts = {
            'email': _('We will use this address only when we need to '
                       'communicate with you about this website - it will not '
                       'be displayed to anyone else. It is recommended to enter '
                       'an email address that is not likely to change in the future.'),
        }


class RecommendModelForm(CaptchaForm, forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = Recommendation

        fields = (
            'profile',
            'reviewer_name',
            'reviewer_institution',
            'reviewer_position',
            'seen_at_conf',
            'comment',
        )

        labels = {
            'profile': _('Recommended Person'),
            'reviewer_name': _('Your full name'),
            'reviewer_institution': _('Your Institution/Company'),
            'reviewer_position': _('Your Position'),
            'seen_at_conf': _('I saw one of her talks'),
            'comment': _('')
        }

        help_texts = {
            'profile': _('Name of the person you would like to recommend'),
            'reviewer_position': _('Please choose the \'closest\' title from '
                                   'the proposed options.'),
            'comment': _('Describe here why you recommend this person for '
                         'conference invitations or collaborations. If you '
                         'attended one of her talks, add details on the event '
                         '(year, event name). Please also mention potential '
                         'conflicts of interest, like personal or '
                         'professional relationships '
                         '(friends, colleagues, former PI, ...)'),
        }

        widgets = {
            'profile': ModelSelect2(
                url='profiles:profiles_autocomplete',
                attrs={
                    'data-minimum-input-length': 3,
                    'data-placeholder': 'Search Profile...',
                },
            )
        }

    def clean(self):
        cleaned_data = super(RecommendModelForm, self).clean()
        profile = cleaned_data.get('profile')
        reviewer_name = cleaned_data.get('reviewer_name')

        if profile \
           and reviewer_name \
           and Recommendation.objects \
                             .filter(profile=profile,
                                     reviewer_name=reviewer_name) \
                             .exists():
            raise forms.ValidationError(_('You have already recommended that '
                                          'person!'),
                                        code='aready_recommended')

        return cleaned_data
