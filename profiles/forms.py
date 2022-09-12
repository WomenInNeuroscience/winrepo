import re
from urllib import parse
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from dal.autocomplete import ModelSelect2
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm as _AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
    UsernameField
)
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from .models import (
    Profile, Recommendation, User, Publication,
    RecommendationQuestionRevision
)


class CaptchaForm(forms.Form):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox, label=False)


class AuthenticationForm(_AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Username or E-mail'}),
    )


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username',
            'name',
            'email',
        )
        help_texts = {
            'email': 'If changed, you will be signed-out and an e-mail will be sent to the new address for confirmation.',
        }


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Old password",
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True}),
    )

    def clean_old_password(self):
        if self.user.password is None:
            return None
        return super().clean_old_password()


class UserProfileForm(forms.ModelForm):

    orcid = forms.CharField(required=False, max_length=200, label='ORCID', help_text='Please insert the information from the brackets: https://orcid.org/[ID]')
    twitter = forms.CharField(required=False, max_length=200, label='Twitter', help_text='Please insert the information from the brackets: https://twitter.com/[username]')
    linkedin = forms.CharField(required=False, max_length=200, label='LinkedIn', help_text='Please insert the information from the brackets: https://linkedin.com/in/[username]')
    github = forms.CharField(required=False, max_length=200, label='GitHub', help_text='Please insert the information from the brackets: https://github.com/[username]')
    google_scholar = forms.CharField(required=False, max_length=200, label='Google Scholar', help_text='Please insert the information from the brackets: https://scholar.google.com/citations?user=[ID]')
    researchgate = forms.CharField(required=False, max_length=200, label='ResearchGate', help_text='Please insert the information from the brackets: https://www.researchgate.net/profile/[username]')

    class Meta:
        model = Profile
        fields = (
            'name',
            'institution',
            'country',
            'contact_email',
            'webpage',
            'position',
            'orcid',
            'twitter',
            'linkedin',
            'github',
            'google_scholar',
            'researchgate',
            'grad_month',
            'grad_year',
            'brain_structure',
            'modalities',
            'methods',
            'domains',
            'keywords',
        )

    def clean(self):
        cleaned_data = super().clean()

        orcid_regex = r'^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9X]{4}$'
        orcid = cleaned_data.get('orcid', '').strip()
        if 'orcid.org' in orcid:
            try:
                [_, _, path, _, _, _] = parse.urlparse(orcid)
                orcid = path.strip('/').split('/')[0]
            except:
                orcid = ''
        if orcid and not re.match(orcid_regex, orcid):
            self.add_error('orcid', 'The ORCID you have provided is not valid. Please check the format specified in the field.')
        else:
            cleaned_data['orcid'] = orcid if orcid else None


        twitter_id_regex = r'^[a-zA-Z0-9_]{1,15}$'
        twitter_id = cleaned_data.get('twitter', '').strip()
        if 'twitter.com' in twitter_id:
            try:
                [_, _, path, _, _, _] = parse.urlparse(twitter_id)
                twitter_id = path.strip('/').split('/')[0]
            except:
                twitter_id = ''
        twitter_id = twitter_id.replace('@', '')
        if twitter_id and not re.match(twitter_id_regex, twitter_id):
            self.add_error('twitter', 'The Twitter ID you have provided is not valid. Please check the format specified in the field.')
        else:
            cleaned_data['twitter'] = twitter_id if twitter_id else None


        linkedin_id_regex = r'^[a-zA-Z0-9\-_]{1,100}$'
        linkedin_id = cleaned_data.get('linkedin', '').strip()
        if 'linkedin.com' in linkedin_id:
            try:
                [_, _, path, _, _, _] = parse.urlparse(linkedin_id)
                linkedin_id = path.strip('/').split('/')[1]
            except:
                linkedin_id = ''
        if linkedin_id and not re.match(linkedin_id_regex, linkedin_id):
            self.add_error('linkedin', 'The Linkedin ID you have provided is not valid. Please check the format specified in the field.')
        else:
            cleaned_data['linkedin'] = linkedin_id if linkedin_id else None


        github_id_regex = r'^[a-zA-Z0-9\-]{1,40}$'
        github_id = cleaned_data.get('github', '').strip()
        if 'github.com' in github_id:
            try:
                [_, _, path, _, _, _] = parse.urlparse(github_id)
                github_id = path.strip('/').split('/')[0]
            except:
                github_id = ''
        if github_id and not re.match(github_id_regex, github_id):
            self.add_error('github', 'The Github ID you have provided is not valid. Please check the format specified in the field.')
        else:
            cleaned_data['github'] = github_id if github_id else None


        google_scholar_id_regex = r'^[a-zA-Z0-9]{1,100}$'
        google_scholar_id = cleaned_data.get('google_scholar', '').strip()
        if google_scholar_id.startswith('https://'):
            params = dict(parse.parse_qsl(parse.urlsplit(google_scholar_id).query))
            google_scholar_id = params.get('user', '')
        if not re.match(google_scholar_id_regex, google_scholar_id):  # try to clean it up
                params = dict(parse.parse_qsl(google_scholar_id))
                if 'user' in params:
                    google_scholar_id = params['user']
                else:
                    google_scholar_id = google_scholar_id.split('&')[0]
        if google_scholar_id and not re.match(google_scholar_id_regex, google_scholar_id):
            self.add_error('google_scholar', 'The Google Scholar URL you have provided is not valid. Please check the format specified in the field.')
        else:
            cleaned_data['google_scholar'] = google_scholar_id if google_scholar_id else None


        researchgate_id_regex = r'^[a-zA-Z0-9_-]{1,100}$'
        researchgate_id = cleaned_data.get('researchgate', '').strip()
        if 'researchgate.net' in researchgate_id:
            try:
                [_, _, path, _, _, _] = parse.urlparse(researchgate_id)
                researchgate_id = path.strip('/').split('/')[1]
            except:
                researchgate_id = ''
        if researchgate_id and not re.match(researchgate_id_regex, researchgate_id):
            self.add_error('researchgate', 'The ResearchGate ID you have provided is not valid. Please check the format specified in the field.')
        else:
            cleaned_data['researchgate'] = researchgate_id if researchgate_id else None


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


class ProfileClaimForm(CaptchaForm, forms.Form):
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

    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.questions = {}
        for field in questions:
            id = f'recommendation_question_{field.id}'
            last_revision = field.last_revision
            options = [
                o.strip()
                for o in last_revision.options.split('\n')
                if o.strip()
            ]

            subfields = []
            for io, option in enumerate(options):
                subfieldsmatch = re.findall(r'\[([^\]]*)\]', option)
                for i, sublabel in enumerate(subfieldsmatch):
                    self.fields[f'{id}_{io}_{i}'] = forms.CharField(
                        label=f'[{sublabel}]' if sublabel else '',
                    )
                    if not sublabel:
                        options[io] = option.replace('[]', '').strip()
                    options[io] = mark_safe(re.sub(r'\[([^\]]*)\]', r"<em>\1</em>", option))
                    subfields.append(f'{id}_{io}_{i}')

            self.questions[id] = {
                'subfields': subfields
            }

            self.fields[id] = \
                forms.MultipleChoiceField(
                    label=last_revision.text,
                    choices=[
                        (i, choice)
                        for i, choice in
                        enumerate(options)
                    ],
                    widget=forms.CheckboxSelectMultiple()
                )


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


class ModelChoiceUserNameField(forms.ModelChoiceField):
    def label_from_instance(self, obj: User) -> str:
        return obj.name


class PublicationAdminForm(forms.ModelForm):

    created_by = ModelChoiceUserNameField(queryset=User.objects.filter(is_staff=True))

    class Meta:
        model = Publication
        fields = ('type', 'title', 'authors', 'description', 'published_at', 'url', 'doi', 'created_by')


class UserAdminForm(forms.ModelForm):

    new_password = forms.CharField(label=_('Password'), widget=forms.PasswordInput, required=False, strip=False)

    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'is_active', 'is_staff', 'is_superuser')


    def save(self, commit=True):
        password = self.cleaned_data["new_password"]
        if password:
            self.instance.set_password(password)
        if commit:
            self.instance.save()
            self._save_m2m()
        else:
            self.save_m2m = self._save_m2m
        return self.instance


class ProfileAdminForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = (
            'is_public', 'name', 'contact_email', 'webpage',
            'institution', 'country', 'position', 'grad_month', 'grad_year',
            'brain_structure', 'modalities', 'methods', 'domains', 'keywords',
            'orcid', 'twitter', 'linkedin', 'github', 'google_scholar', 'researchgate'
        )


class RecommendationQuestionRevisionForm(forms.ModelForm):

    class Meta:
        model = RecommendationQuestionRevision
        fields = ('text', 'options', 'multiple')
