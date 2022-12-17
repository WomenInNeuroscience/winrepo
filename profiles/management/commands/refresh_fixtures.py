import random
from django.core import management
from django.core.management.base import BaseCommand, CommandError

import recurrence
from recurrence import Recurrence, Rule

import pytz
from datetime import datetime, date, time, timedelta

import winrepo.settings as settings
from profiles.models import Country, User, Profile, Recommendation, Publication, Event
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
            countries_data = [c.split('\t') for c in f.read().splitlines() if c]

        Country.objects.all().delete()

        countries = []
        for code, name, under in countries_data:
            is_under_represented = under == '1'

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
                orcid='orcid',
                twitter='twitter',
                linkedin='linkedin',
                github='github',
                google_scholar='google_scholar',
                researchgate='researchgate',
            )
            profiles += [profile]
            profile.save()

        random_words = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. ' \
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
                random_words[0:2] + \
                list(random.sample(random_words[2:], 20))
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
            username='admin',
            name='Admin',
            email='admin@winrepo.org',
            password='admin',
            is_staff=True,
            is_superuser=True,
        )
        user.save()

        user = User.objects.create_user(
            username='user',
            name='Shaquille Oatmeal',
            email='user@winrepo.org',
            password='user',
        )
        user.save()

        user = User.objects.create_user(
            username='user-profile',
            name='Lorie C. Salas',
            email='user-profile@winrepo.org',
            password='user',
            is_staff=True,
            is_superuser=True,
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

        pub = Publication(
            type='JP',
            title='Characteristics of Faculty Position Advertisements Associated with Applicant Diversity',
            authors='Schmaling, K. B.\nBlume, A. W.\nBaker, D. L.',
            published_at='2017-01-01',
            url='http://digitalcommons.www.na-businesspress.com/JHETP/JHETP17-8/SchmalingKB_17_8.pdf',
            doi=None,
            created_by=user,
        )
        pub.save()

        pub = Publication(
            type='JP',
            title='Can We Reduce Bias in the Recruiting Process and Diversify Pools of Candidates by Using Different Types of Words in Job Descriptions?',
            authors='Collier, D.\nZhang, C.',
            published_at='2016-01-01',
            url='https://hdl.handle.net/1813/74363',
            doi=None,
            created_by=user,
        )
        pub.save()

        pub = Publication(
            type='JP',
            title='Diversifying collaboration networks to increase equity in psychology',
            authors='Hsiung Wojcik, E.',
            published_at='2022-01-01',
            url='https://www.nature.com/articles/s44159-021-00014-y',
            doi='10.1038/s44159-021-00014-y',
            created_by=user,
        )
        pub.save()

        for (k, _) in Publication.Type.choices:

            for _ in range(10):

                title = ' '.join(
                    random.sample(random_words[2:], 6)
                ).capitalize()

                authors = []
                for i in range(4):
                    name = random.choice(names)[0]
                    surname = random.choice(surnames)
                    authors += [f'{surname}, {name}']
                authors = '\n'.join(authors)

                year = str(random.randint(1950, 2020))
                published_at = year + '-01-01'

                uid = ('-'.join(
                    random.sample(random_words[2:], 2)
                )).lower()
                doi = f'10.{year}/' + uid

                site = None
                if k != Publication.Type.JOURNAL_PAPER:
                    site = 'https://site.com/articles/' + uid
                
                pub = Publication(
                    type=k,
                    title=title,
                    authors=authors,
                    published_at=published_at,
                    url=site,
                    doi=doi,
                    created_by=user,
                )
                pub.save()



        RULE = Rule(recurrence.WEEKLY)
        PATTERN = Recurrence(
            rrules=[RULE]
        )


        timezone = pytz.timezone("UTC")
        event_starts = date.today() + timedelta(days=3)

        event = Event(
            created_at=datetime.combine(event_starts, time(hour=9, tzinfo=timezone)),
            created_by=user,
            start_date=datetime.combine(event_starts, time(hour=4, tzinfo=timezone)),
            end_date=datetime.combine(event_starts + timedelta(weeks=20), time(hour=11, tzinfo=timezone)),
            title="Weekly Meeting",
            type=Event.Type.PANEL_DISCUSSION,
            description="The board weekly meeting",
            location="https://zoom.us/j/123456789",
            recurrence=PATTERN,
        )
        event.save()

        event = Event(
            created_at=datetime.combine(event_starts, time(hour=9, tzinfo=timezone)),
            created_by=user,
            start_date=datetime.combine(event_starts, time(hour=9, tzinfo=timezone)),
            end_date=datetime.combine(event_starts + timedelta(weeks=2), time(hour=11, tzinfo=timezone)),
            title="Overlapping Recurrent Meeting",
            type=Event.Type.TALK,
            recurrence=PATTERN,
        )
        event.save()

        event = Event(
            created_at=datetime.combine(event_starts, time(hour=9)),
            created_by=user,
            start_date=datetime.combine(event_starts, time(hour=9)),
            end_date=datetime.combine(event_starts, time(hour=19)),
            title="One Time Conference",
            type=Event.Type.CONFERENCE,
        )
        event.save()

        event = Event(
            created_at=datetime.combine(event_starts, time(hour=9)),
            created_by=user,
            start_date='2023-07-22 14:00:00+00:00',
            end_date='2023-07-26 23:00:00+00:00',
            title="OHBM",
            type=Event.Type.CONFERENCE,
        )
        event.save()


        management.call_command(
            'dumpdata',
            'profiles',
            'auth',
            natural_primary=True,
            natural_foreign=True,
            output='profiles/fixtures/winrepo.json'
        ) 
