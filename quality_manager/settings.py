import os
from m3_legacy import config


PROJECT_ROOT = os.path.dirname(__file__)
STATIC_ROOT = os.path.join(PROJECT_ROOT, '../../static')

conf = config.ProjectConfig(
    filenames=[
        os.getenv('WEB_BB_CONF') or os.path.normpath(os.path.join(PROJECT_ROOT, 'configs.conf')),
    ])

ROOT_URL = conf.get('urls', 'ROOT')
# Абсолютный путь и url до пользовательских фалов.
DOWNLOADS_DIR = conf.get('static', 'DOWNLOADS')
DOWNLOADS_URL = conf.get('urls', 'DOWNLOADS')
MEDIA_ROOT = DOWNLOADS_DIR
MEDIA_URL = DOWNLOADS_URL

DESKTOP_HTML = conf.get('style', 'DESKTOP_HTML_NAME')


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u^iu*dm#kj@1^t*s#kaak9m=47d=(@%@9nxu5i&o^flx$2%r&o'

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
    'team_management',
    'm3',
    'm3_ext',
    'm3_ext.ui',
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

ROOT_URLCONF = 'quality_manager.urls'

default_template_loaders = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'm3_ext.ui.js_template_loader.Loader',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,
                              'quality_manager/../quality_manager/templates',
                              )],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "django.template.context_processors.media",
                "django.template.context_processors.static",
            ],
            'loaders': default_template_loaders,
        },
    },
]

WSGI_APPLICATION = 'quality_manager.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': conf.get('database', 'DATABASE_ENGINE'),
        'NAME': conf.get('database', 'DATABASE_NAME'),
        'USER': conf.get('database', 'DATABASE_USER'),
        'PASSWORD': conf.get('database', 'DATABASE_PASSWORD'),
        'HOST': conf.get('database', 'DATABASE_HOST'),
        'PORT': conf.get('database', 'DATABASE_PORT'),
        'DISABLE_SERVER_SIDE_CURSORS':
            conf.get_bool('database', 'DATABASE_DISABLE_SERVER_SIDE_CURSORS'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
