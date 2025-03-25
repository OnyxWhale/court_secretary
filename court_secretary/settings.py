from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-yfo)%$dtcdynbu#+te4as-wo2j34x-p#m-j@!w!7xj$weq+kw+'

# SECURITY WARNING: don't run with debug turned on in production!
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

# Настройка логирования
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'app.log'

# Создаем директорию и файл, если они не существуют
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
            'filename': str(LOG_FILE),  # Преобразуем Path в строку
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