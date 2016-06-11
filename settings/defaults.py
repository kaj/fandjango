# Django settings for fandjango project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = False

ADMINS = (
    ('Rasmus Kaj', 'kaj@kth.se'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'fandjango',
        'USER': 'fandjango',
        'PASSWORD': '',
        'HOST': '',                      # Set to empty string for localhost.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Stockholm'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'sv-se'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'APP_DIRS': True,
        'OPTIONS': {
            #'environment': 'blog.util.environment',
            'extensions': [
                #'jinja2.ext.i18n',
                #'compressor.contrib.jinja2ext.CompressorExtension',
                #'blog.util.FragmentCacheExtension',
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    'ssladmin.middleware.SSLAdmin',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'libris',
)

import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

FORWARDS = {
    '/favicon.ico':            '/static/goda-16.png',
    '/rick_o_shay':            '/rick_oshay',
    '/what/christophe_d_errant': '/what/christophe_derrant',
    '/what/julie':             '/fa/17.1',
    '/what/mystiska_2_an':     '/what/mystiska_2an',
    '/what/nelson_n_dela':     '/what/nelson_ndela',
    '/what/rhodiska_urbefolkningens_frihetstrupper': '/what/rba',
    '/who/arthur_conan_doyle': '/who/sir_arthur_conan_doyle',
    '/who/mikael_frenneson':   '/who/mikael_frennesson',
    '/who/sir_a_conan_doyle':  '/who/sir_arthur_conan_doyle',
    '/who/y_sente':            '/who/yves_sente',
}
