from .common import *

SECRET_KEY = os.getenv("PAYESHGAR_SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    'monitoring',
    'inspecting',

    'rest_framework',
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

ROOT_URLCONF = 'payeshgar_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'payeshgar_server.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = False

CELERY_BROKER_URL = "amqp://{rabbitmq_hostname}:{rabbitmq_port}".format(
    rabbitmq_hostname=os.environ.get("PAYESHGAR_RABBITMQ_HOSTNAME", "localhost"),
    rabbitmq_port=os.environ.get("PAYESHGAR_RABBITMQ_PORT", "5672"),
)

ENVIRONMENT = os.getenv("PAYESHGAR_ENVIRONMENT", "PRODUCTION")

if ENVIRONMENT == "PRODUCTION":
    from . import production
elif ENVIRONMENT == "DEVELOPMENT":
    from . import development

try:
    from payeshgar_server.settings.local_settings import *
except:
    pass
