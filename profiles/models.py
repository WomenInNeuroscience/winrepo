from adminsortable.fields import SortableForeignKey
from adminsortable.models import SortableMixin
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.manager import BaseManager
from django.db.models.query import QuerySet
from django.utils import timezone
from multiselectfield import MultiSelectField

PHD = 'PhD student'
MDR = 'Medical Doctor'
PDR = 'Post-doctoral researcher'
JRE = 'Researcher/ scientist'
SRE = 'Senior researcher/ scientist'
LEC = 'Lecturer'
ATP = 'Assistant Professor'
ACP = 'Associate Professor'
PRF = 'Professor'
DIR = 'Group leader/ Director/ Head of Department'

POSITION_CHOICES = (
    (PHD, 'PhD student'),
    (MDR, 'Medical Doctor'),
    (PDR, 'Post-doctoral researcher'),
    (JRE, 'Researcher/ scientist'),
    (SRE, 'Senior researcher/ scientist'),
    (LEC, 'Lecturer'),
    (ATP, 'Assistant Professor'),
    (ACP, 'Associate Professor'),
    (PRF, 'Professor'),
    (DIR, 'Group leader/ Director/ Head of Department')
)

MONTHS_CHOICES = (
    ('01', 'January'),
    ('02', 'February'),
    ('03', 'March'),
    ('04', 'April'),
    ('05', 'May'),
    ('06', 'June'),
    ('07', 'July'),
    ('08', 'August'),
    ('09', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December')
)

STRUCTURE_CHOICES = (
    ('N', 'Neuron'),
    ('L', 'Layer'),
    ('C', 'Column'),
    ('R', 'Region'),
    ('W', 'Whole Brain')
)

MODALITIES_CHOICES = (
    ('EP', 'Electrophysiology (EEG, MEG, ECoG)'),
    ('OE', 'Other electrophysiology'),
    ('MR', 'MRI'),
    ('PE', 'PET'),
    ('DT', 'DTI'),
    ('BH', 'Behavioural'),
    ('ET', 'Eye Tracking'),
    ('BS', 'Brain Stimulation'),
    ('GT', 'Genetics'),
    ('FN', 'fNIRS'),
    ('LE', 'Lesions and Inactivations'),
)

METHODS_CHOICES = (
    ('UV', 'Univariate'),
    ('MV', 'Multivariate'),
    ('PM', 'Predictive Models'),
    ('DC', 'DCM'),
    ('CT', 'Connectivity'),
    ('CM', 'Computational Modeling'),
    ('AM', 'Animal Models')
)

DOMAINS_CHOICES = (
    ('CG', 'Cognition (general)'),
    ('MM', 'Memory'),
    ('SS', 'Sensory systems'),
    ('MO', 'Motor Systems'),
    ('LG', 'Language'),
    ('EM', 'Emotion'),
    ('PN', 'Pain'),
    ('LE', 'Learning'),
    ('AT', 'Attention'),
    ('DE', 'Decision Making'),
    ('DV', 'Developmental'),
    ('SL', 'Sleep'),
    ('CN', 'Consciousness'),
    ('CL', 'Clinical (general)'),
    ('DM', 'Dementia'),
    ('PK', 'Parkinson'),
    ('DD', 'Other degenerative diseases'),
    ('PS', 'Psychiatry'),
    ('AD', 'Addiction'),
    ('ON', 'Oncology'),
    ('EV', 'Evolutionary'),
    ('CM', 'Cellular and Molecular'),
    ('BI', 'Bioinformatics'),
    ('NC', 'Neuropharmacology'),
    ('ET', 'Ethics')
)

POSITION_CHOICES = (
    ('PhD student', 'PhD student'),
    ('Medical Doctor', 'Medical Doctor'),
    ('Post-doctoral researcher', 'Post-doctoral researcher'),
    ('Senior researcher/ scientist', 'Senior researcher/ scientist'),
    ('Lecturer', 'Lecturer'),
    ('Assistant Professor', 'Assistant Professor'),
    ('Associate Professor', 'Associate Professor'),
    ('Professor', 'Professor'),
    ('Group leader/ Director/ Head of Department', 'Group leader/ Director/ Head of Department'),
)


PUBLICATION_TYPE = (
    ('peer-reviewed-paper', 'Peer-reviewed Paper'),
    ('report', 'Report'),
    ('preprint', 'Preprint'),
    ('book', 'Book'),
    ('blog-post', 'Blog Post')
)


class EnumField(models.CharField):

    # TODO update all enum fields to use this

    def __init__(self, enum=None, *args, **kwargs):
        self.enum = enum
        if enum:
            kwargs['choices'] = enum.choices
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value is not None:
            return self.enum(value)

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        return self.to_python(value)


class Country(models.Model):
    code = models.CharField(max_length=3, blank=False, unique=True)
    name = models.CharField(max_length=60, blank=False)
    is_under_represented = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'countries'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))

        extra_fields.setdefault('is_active', True)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    username = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    password = models.CharField(max_length=128, null=True)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def first_name(self):
        try:
            return self.name.partition(' ')[0]
        except:
            return self.name

    @property
    def any_claimed_profile(self):
        try:
            Profile.all_objects.values('id').get(
                claimed_by=self,
                claimed_at__isnull=False
            )
            return True
        except Profile.DoesNotExist:
            return False

    def check_password(self, raw_password):
        if self.password:
            return super().check_password(raw_password)
        return False


class ProfileManager(models.Manager):

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return ProfileQuerySet(self.model).filter(deleted_at=None)
        return ProfileQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class ProfileQuerySet(QuerySet):
    def delete(self):
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)


class Profile(models.Model):

    objects = ProfileManager()
    all_objects = ProfileManager(alive_only=False)

    @classmethod
    def get_position_choices(cls):
        return POSITION_CHOICES

    @classmethod
    def get_structure_choices(cls):
        return STRUCTURE_CHOICES

    @classmethod
    def get_modalities_choices(cls):
        return MODALITIES_CHOICES

    @classmethod
    def get_methods_choices(cls):
        return METHODS_CHOICES

    @classmethod
    def get_domains_choices(cls):
        return DOMAINS_CHOICES

    user = models.OneToOneField(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='profile'
    )
    is_public = models.BooleanField(default=True)

    name = models.CharField(max_length=200, blank=False)
    contact_email = models.EmailField(verbose_name='Contact E-mail', blank=True)
    webpage = models.URLField(blank=True)
    institution = models.CharField(max_length=100, blank=False)
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                related_name='profiles',
                                null=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES,
                                blank=True)
    grad_month = models.CharField(verbose_name='Month', max_length=2,
                                  choices=MONTHS_CHOICES, blank=True)
    grad_year = models.CharField(verbose_name='Year', max_length=4, blank=True)
    brain_structure = MultiSelectField(choices=STRUCTURE_CHOICES, blank=True)
    modalities = MultiSelectField(choices=MODALITIES_CHOICES, blank=True)
    methods = MultiSelectField(choices=METHODS_CHOICES, blank=True)
    domains = MultiSelectField(choices=DOMAINS_CHOICES, blank=True)
    keywords = models.CharField(max_length=250, blank=True)

    orcid = models.CharField(null=True, blank=True, verbose_name='ORCID', max_length=30, help_text='Please insert the information from the brackets: https://orcid.org/[ID]')
    twitter = models.CharField(null=True, blank=True, max_length=200, help_text='Please insert the information from the brackets: https://twitter.com/[username]')
    linkedin = models.CharField(null=True, blank=True, verbose_name='LinkedIn', max_length=200, help_text='Please insert the information from the brackets: https://linkedin.com/in/[username]')
    github = models.CharField(null=True, blank=True, verbose_name='GitHub', max_length=200, help_text='Please insert the information from the brackets: https://github.com/[username]')
    google_scholar = models.CharField(null=True, blank=True, verbose_name='Google Scholar', max_length=200, help_text='Please insert the information from the brackets: https://scholar.google.com/citations?user=[ID]')
    researchgate = models.CharField(null=True, blank=True, verbose_name='ResearchGate', max_length=200, help_text='Please insert the information from the brackets: https://www.researchgate.net/profile/[username]')

    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    claimed_at = models.DateTimeField(null=True)
    claimed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='profile_claims',
        null=True
    )

    class Meta:
        ordering = ['name', 'institution', 'updated_at']
        base_manager_name = 'objects'

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super().delete()

    def __str__(self):
        return f'{self.name}, {self.institution}'

    def brain_structure_labels(self):
        return [dict(STRUCTURE_CHOICES).get(item, item)
                for item in self.brain_structure]

    def modalities_labels(self):
        return [dict(MODALITIES_CHOICES).get(item, item)
                for item in self.modalities]

    def methods_labels(self):
        return [dict(METHODS_CHOICES).get(item, item)
                for item in self.methods]

    def domains_labels(self):
        return [dict(DOMAINS_CHOICES).get(item, item)
                for item in self.domains]

    def grad_month_labels(self):
        return dict(MONTHS_CHOICES).get(self.grad_month)


class RecommendationQuerySet(QuerySet):
    pass


class RecommendationManager(models.Manager):

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return RecommendationQuerySet(self.model).filter(profile__deleted_at=None)
        return RecommendationQuerySet(self.model)


class Recommendation(models.Model):

    profile = models.ForeignKey(Profile,
                                on_delete=models.CASCADE,
                                related_name='recommendations')

    reviewer = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='recommended'
    )
    reviewer_name = models.CharField(max_length=100, blank=False)
    reviewer_email = models.EmailField(blank=True)
    reviewer_position = models.CharField(max_length=50,
                                         choices=POSITION_CHOICES,
                                         blank=True)
    reviewer_institution = models.CharField(max_length=100, blank=False)
    seen_at_conf = models.BooleanField(null=True)
    comment = models.TextField(blank=False)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.comment[:50]


class SoftDeleteQuerySet(QuerySet):

    def delete(self):
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)


class SoftDeleteManager(BaseManager.from_queryset(SoftDeleteQuerySet)):

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return super().get_queryset().filter(deleted_at=None)
        return super().get_queryset()

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class SoftDeleteModel(models.Model):

    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager(alive_only=False)

    deleted_at = models.DateTimeField(null=True, editable=False)


class RecommendationQuestion(SoftDeleteModel):

    last_revision = models.ForeignKey(
                        'RecommendationQuestionRevision',
                        on_delete=models.DO_NOTHING,
                        related_name='last_revision',
                        null=True,
                    )


class RecommendationQuestionRevision(SortableMixin):

    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        editable=False,
        db_index=True
    )

    question = models.ForeignKey(RecommendationQuestion,
                                on_delete=models.CASCADE,
                                related_name='revisions')


    revision = models.IntegerField('Revision', db_index=True)
    text = models.CharField(max_length=280, blank=False)

    options = models.TextField(blank=False)
    multiple = models.BooleanField(default=False)


    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='recommendation_questions',
        null=True
    )

    class Meta:
        verbose_name = ' Recommendation Question'
        verbose_name_plural = ' Recommendation Questions'
        ordering = ['order']


    def save(self, *args, **kwargs):
        self.options = '\n'.join(filter(None, [
            line.strip() for line in self.options.split('\n')
        ]))

        super().save(*args, **kwargs)
        
        self.question.last_revision = self
        self.question.save()


class RecommendationAnswer(models.Model):

    recommendation = models.ForeignKey(Recommendation,
                                       on_delete=models.CASCADE,
                                       related_name='answers')

    question = models.ForeignKey(RecommendationQuestionRevision,
                                 on_delete=models.CASCADE,
                                 related_name='answers')

    answer = models.TextField(blank=False)

    def __str__(self):
        return self.answer


class Publication(models.Model):

    class Type(models.TextChoices):
        JOURNAL_PAPER = 'JP', 'Journal Paper'
        REPORT = 'RE', 'Report'
        PREPRINT = 'PP', 'Preprint'
        BOOK = 'BO', 'Book'
        BLOG_POST = 'BP', 'Blog Post'
        NEWS = 'NE', 'News/Magazine'

    type = EnumField(
        enum=Type,
        max_length=2,
        blank=False
    )
    title = models.CharField(max_length=200, blank=False)
    authors = models.TextField(blank=False, help_text='First Middle Last → Last, F. M.<br>One author per line.')
    description = models.TextField(null=True, blank=True)
    published_at = models.DateField(blank=False, help_text='')

    url = models.URLField(verbose_name='URL', null=True, blank=True)
    doi = models.CharField(max_length=200, verbose_name='DOI', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='publications',
        null=True
    )

    @property
    def formatted_authors(self):
        return [a.strip() for a in self.authors.split('\n')]

    class Meta:
        ordering = ['-published_at']
