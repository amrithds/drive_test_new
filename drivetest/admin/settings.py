"""
Django settings for admin project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-iuz1mwz3yfh4cttpm7j+=rm+#+t5h07k^zsr73z!v)qgqkoca^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'course',
    'report',
    'app_config'
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'PAGE_SIZE': 1000,
    
}

CORS_ALLOWED_ORIGINS = [
   "http://localhost:4200",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'course.middleware.DisableCSRFMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'admin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'admin.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
    "ENGINE": "django.db.backends.mysql",
    "NAME": "driver_test",
    "USER":"root",
    #"PASSWORD":"rootpass",
    "PASSWORD":"F2s@btm2",
    "HOST":"127.0.0.1",
    "PORT":"3306",
    "OPTIONS" : {
            "init_command": "SET foreign_key_checks = 0;",
        }
    }
}

#LOG settings
LOG_DIR = os.path.join(BASE_DIR, 'log')

DEFAULT_LOG_FILE = '/log.log'
RF_LOG_FILE = '/rfLog.log'
SENSOR_LOG_FILE = '/sensor.log'
REPORT_LOG_FILE = '/report.log'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
    "standard": {
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level":"DEBUG",
            "class":"logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR + DEFAULT_LOG_FILE,
            "maxBytes": 1024*1024*5, # 5 MB
            "backupCount": 5,
            "formatter":"standard",
        },
        "sensorLog": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR + SENSOR_LOG_FILE,
            "maxBytes": 1024*1024*5, # 5 MB
            "backupCount": 5,
            "formatter":"standard",
        },
        "reportLog": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR + REPORT_LOG_FILE,
            "maxBytes": 1024*1024*5, # 5 MB
            "backupCount": 5,
            "formatter":"standard",
        },
        "RFLog": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR + RF_LOG_FILE,
            "maxBytes": 1024*1024*5, # 5 MB
            "backupCount": 5,
            "formatter":"standard",
        },
    },
    "loggers": {
        "default": {
            "handlers": ["default"],
            "level": "ERROR",
            "propagate": True
        },
        "sensorLog": {
            "handlers": ["sensorLog"],
            "level": "DEBUG",
            "propagate": True,
        },
        "reportLog": {
            "handlers": ["reportLog"],
            "level": "DEBUG",
            "propagate": True,
        },
        "RFLog": {
            "handlers": ["RFLog"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT=os.path.join(BASE_DIR, 'static/')
MEDIA_URL='/media/'
MEDIA_ROOT=os.path.join(BASE_DIR, 'media/')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'course.User'
# LOGIN_REDIRECT_URL="/"
APPEND_SLASH=True

SESSION_COOKIE_SECURE=False
LIST_PER_PAGE = 5
PAGINATE_BY=5
#get data from data generator
# ENABLE_DATA_GENERATOR = True
CORS_ORIGIN_ALLOW_ALL = DEBUG
# CORS_ALLOWED_ORIGIN = [
#     "http://localhost:4200",
#     "http://127.0.0.1:4200",
# ]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache/'),
    }
}