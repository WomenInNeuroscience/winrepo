import os
import time
from decouple import config

STATIC_VERSION = int(time.time())  # Unique timestamp to force reload

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ENV = config('ENV', default='Local')

ALLOWED_HOSTS = \
    ['*'] \
    if DEBUG else \
    ['localhost', '127.0.0.1', 'winrepo.org', 'www.winrepo.org', 'winrepo.pythonanywhere.com']

INSTALLED_APPS = [
    'multiselectfield',
    'django_bootstrap5',
    "crispy_forms",
    "crispy_bootstrap5",
    'captcha',
    'dal',
    'dal_select2',
    'robots',
    'rest_framework',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django_extensions',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.twitter',

    'profiles',
    'django.contrib.admin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'winrepo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [(os.path.join(BASE_DIR, 'templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'winrepo.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE'),
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'TEST': {
            'NAME': config('DB_TEST_NAME'),
        }
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = 'profiles:user'
LOGOUT_REDIRECT_URL = 'profiles:home'

AUTH_USER_MODEL = 'profiles.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation'
                '.MinimumLengthValidator',
    },
    {
        'NAME': 'profiles.password_validation.LowercaseValidator',
    },
    {
        'NAME': 'profiles.password_validation.UppercaseValidator',
    },
    {
        'NAME': 'profiles.password_validation.NumberValidator',
    },
    {
        'NAME': 'profiles.password_validation.SymbolValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'profiles.backends.EmailOrUsernameModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_ADAPTER = 'profiles.adapter.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'profiles.adapter.SocialAccountAdapter'
SOCIALACCOUNT_PRESERVE_USERNAME_CASING = False
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),
            'secret': config('GOOGLE_CLIENT_SECRET'),
        }
    },
    'twitter': {
        'APP': {
            'client_id': config('TWITTER_CLIENT_ID'),
            'secret': config('TWITTER_CLIENT_SECRET'),
        }
    },
    'github': {
        'SCOPE': [
            'user',
        ],
        'APP': {
            'client_id': config('GITHUB_CLIENT_ID'),
            'secret': config('GITHUB_CLIENT_SECRET'),
        }
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "static-collected")

RECAPTCHA_PUBLIC_KEY = config('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = config('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_DOMAIN = config('RECAPTCHA_DOMAIN')

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
SENDGRID_API_KEY = config('SENDGRID_API_KEY', default='')
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default='').lower() == 'true'
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default='').lower() == 'true'
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=60, cast=int)

EMAIL_FROM = config('DEFAULT_FROM_EMAIL')
EMAIL_REPLY_TO = config('DEFAULT_REPLY_TO_EMAIL')
EMAIL_SUBJECT_PREFIX = 'WiNRepo - '

SITE_ID = config('SITE_ID', cast=int, default=1)
ROBOTS_CACHE_TIMEOUT = 60 * 60 * 24

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

SELECT2_CSS = ''

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ]
}

if DEBUG:
    SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

    LOGGING = {
        'version': 1,
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'filters': ['require_debug_true'],
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            }
        }
    }

if ENV != 'Local':
    SECURE_SSL_REDIRECT = True
