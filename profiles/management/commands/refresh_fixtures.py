import random
from django.core import management
from django.core.management.base import BaseCommand, CommandError

import winrepo.settings as settings
from profiles.models import Country, User, Profile, Recommendation
from profiles.models import (
    STRUCTURE_CHOICES,
    MODALITIES_CHOICES,
    METHODS_CHOICES,
    DOMAINS_CHOICES,
    MONTHS_CHOICES,
    POSITION_CHOICES,
)

class Command(BaseCommand):
    help = 'Re-create fixtures based on models'

    def add_arguments(self, parser):
        parser.add_argument('--seed', default=1, type=int, help='Random Seed')
        parser.add_argument('--profiles', default=10, type=int, help='Number of profiles to be created')

    def handle(self, *args, **kwargs):

        if not settings.DEBUG:
            raise CommandError('Please, do not run this command on production mode. It will wipe the database.')

        random.seed(kwargs['seed'])

        management.call_command(
            'flush',
            no_input=True,
            interactive=False,
        )

        countries_data = []
        with open('profiles/fixtures/countries.txt') as f:
            countries_data = [c.split('\t') for c in f.read().splitlines()]

        Country.objects.all().delete()

        countries = []
        for name, code in countries_data:
            is_under_represented = random.random() > 0.5

            country =  Country(
                code=code,
                name=name,
                is_under_represented=is_under_represented,
            )
            country.save()
            countries += [country]


        institutions = []
        with open('profiles/fixtures/institutions.txt') as f:
            institutions = f.read().splitlines()


        names = []
        surnames = []
        with open('profiles/fixtures/names.txt') as f:
            fullnames = [n.split(' ') for n in f.read().splitlines()]
            names = [n[0] for n in fullnames]
            surnames = [n[1] for n in fullnames]


        Profile.objects.all().delete()

        n_profiles = kwargs['profiles']
        profiles = []
        for _ in range(n_profiles):

            brain_structure = random.choice(STRUCTURE_CHOICES)[0]
            modalities = random.choice(MODALITIES_CHOICES)[0]
            methods = random.choice(METHODS_CHOICES)[0]
            domains = random.choice(DOMAINS_CHOICES)[0]

            grad_month = random.choice(MONTHS_CHOICES)[0]
            grad_year = str(random.randint(1950, 2020))

            name = random.choice(names)
            surname = random.choice(surnames)
            fullname = name + ' ' + surname
            institution = random.choice(institutions)
            slug = fullname.lower().replace(' ', '-')
            email = slug + '@' + institution.lower().replace(' ', '-') + '.edu'

            position = random.choice(POSITION_CHOICES)[0]

            profile = Profile(
                name=fullname,
                contact_email=email,
                webpage='http://' + slug + '.me',
                institution=institution,
                country=random.choice(countries),
                position=position,
                grad_month=grad_month,
                grad_year=grad_year,
                brain_structure=brain_structure,
                modalities=modalities,
                methods=methods,
                domains=domains,
                keywords='',
            )
            profiles += [profile]
            profile.save()

        recommendation_words = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. ' \
        'Curabitur maximus, elit in ornare convallis, eros mi pharetra erat, ' \
        'sed dictum dolor nulla viverra odio. Vivamus pulvinar blandit massa ' \
        'ac facilisis. Ut et odio fringilla, dictum tellus non, aliquam est.' \
        'Maecenas aliquet in sem vel vestibulum. Nullam ornare pulvinar malesuada. ' \
        'Donec massa urna, dapibus ut arcu ut, aliquet consequat orci. Donec ' \
        'gravida ut ligula fringilla ullamcorper. Mauris quis lacinia augue. ' \
        'In hac habitasse platea dictumst. Praesent et iaculis neque. ' \
        'Vestibulum dignissim.'.split(' ')

        for profile in profiles:

            name = random.choice(names)
            surname = random.choice(surnames)
            fullname = name + ' ' + surname
            institution = random.choice(institutions)
            slug = fullname.lower().replace(' ', '-')
            email = slug + '@' + institution.lower().replace(' ', '-') + '.edu'
            position = random.choice(POSITION_CHOICES)[0]

            recommendation = ' '.join(
                recommendation_words[0:2] + \
                list(random.sample(recommendation_words[2:], 20))
            )

            Recommendation(
                profile=profile,
                reviewer_name=fullname,
                reviewer_email=email,
                reviewer_position=position,
                reviewer_institution=institution,
                seen_at_conf=True,
                comment=recommendation,
            ).save()


        # Accounts

        user = User.objects.create_user(
            name='User Resu',
            email='anibalsolon@gmail.com',
            password='user'
        )
        user.save()

        user = User.objects.create_user(
            name='User Resu',
            email='user-profile@winrepo.org',
            password='user'
        )
        user.save()

        position = random.choice(POSITION_CHOICES)[0]
        brain_structure = random.choice(STRUCTURE_CHOICES)[0]
        modalities = random.choice(MODALITIES_CHOICES)[0]
        methods = random.choice(METHODS_CHOICES)[0]
        domains = random.choice(DOMAINS_CHOICES)[0]

        grad_month = random.choice(MONTHS_CHOICES)[0]
        grad_year = str(random.randint(1950, 2020))

        profile = Profile(
            user=user,
            name='User Resu',
            contact_email='user-profile@winrepo.org',
            webpage='http://user-resu.me',
            institution='User University',
            country=random.choice(countries),
            position=position,
            grad_month=grad_month,
            grad_year=grad_year,
            brain_structure=brain_structure,
            modalities=modalities,
            methods=methods,
            domains=domains,
            keywords='',
        )
        profile.save()


        management.call_command(
            'dumpdata',
            'profiles',
            'auth',
            natural_primary=True,
            natural_foreign=True,
            output='profiles/fixtures/winrepo.json'
        ) 
