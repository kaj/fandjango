# Django settings for fandjango project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Rasmus Kaj', 'kaj@kth.se'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
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

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'libris',
)

STATIC_URL = '/static/'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

FORWARDS = {
    '/rick_o_shay':            '/rick_oshay',
    '/what/christophe_d_errant': '/what/christophe_derrant',
    '/what/julie':             '/fa/17.1',
    '/what/mystiska_2_an':     '/what/mystiska_2an',
    '/what/nelson_n_dela':     '/what/nelson_ndela',
    '/what/rhodiska_urbefolkningens_frihetstrupper': '/what/rba',
    '/who/arthur_conan_doyle': '/who/sir_arthur_conan_doyle',
    '/who/mikael_frenneson':   '/who/mikael_frennesson',
    '/who/sir_a_conan_doyle':  '/who/sir_arthur_conan_doyle',
    '/who/yves_sente':         '/who/yves_sente',
}
