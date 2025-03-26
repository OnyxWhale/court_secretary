from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-yfo)%$dtcdynbu#+te4as-wo2j34x-p#m-j@!w!7xj$weq+kw+'
DEBUG = True
ALLOWED_HOSTS = ['109.120.178.123', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'web',
    'parser',
    'summary',
    'judges',
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

ROOT_URLCONF = 'court_secretary.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'court_secretary_db',
        'USER': 'court_user',
        'PASSWORD': 'court_password',
        'HOST': 'db',
        'PORT': '5432',
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = ['static']
STATIC_ROOT = '/app/staticfiles'

SCHEDULED_PARSING_INTERVAL = 3600
FORUM_URL = "https://forum.gta5rp.com/forums/federalnyj-sud.1745/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
URGENT_THREAD_THRESHOLD_HOURS = 50
TRIAL_DURATION_THRESHOLD_HOURS = 120

# Логирование
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'app.log'

if not LOG_DIR.exists():
    os.makedirs(LOG_DIR)
if not LOG_FILE.exists():
    LOG_FILE.touch()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOG_FILE),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'court_secretary': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}