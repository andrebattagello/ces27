import os
import django
try:
    from secret import *
except:
    pass

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

SITE_ID = 1
SITE_URL = 'localhost'

INTERNAL_IPS = ('127.0.0.1',)

# Make this unique, and don't share it with anybody.
#With django-extensions generate a new one using `manage.py generate_secret_key`
SECRET_KEY = ''

ROOT_URLCONF = 'urls'

###############################################
##General Project information
PROJECT_NAME = 'ces27'
PROJECT_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..')
SRC_ROOT = os.path.join(PROJECT_ROOT, 'src')
APPS_ROOT = os.path.join(SRC_ROOT, 'apps')
DOCS_ROOT = os.path.join(PROJECT_ROOT, 'docs')
PUBLIC_ROOT = os.path.join(PROJECT_ROOT, 'public')
TEMPLATES_ROOT = os.path.join(PROJECT_ROOT, 'templates')
###############################################


###############################################
##Language support settings
USE_I18N = True
USE_L10N = True
#TIME_ZONE = 'America/Chicago'
#LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Sao_Paulo'
LANGUAGE_CODE = 'pt-br'
USE_TZ = True
###############################################


###############################################
##Media assets (user-uploaded content) settings
MEDIA_ROOT = os.path.join(PUBLIC_ROOT, 'media')
MEDIA_URL = '/media/'
###############################################


###############################################
##Static assets settings
STATIC_ROOT = os.path.join(PUBLIC_ROOT, 'static')  # collect to this directory
STATIC_URL = '/static/'  # serve them from this URL
#ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
#search them from this directories
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),
    #uncomment the next line if using the admin django contrib app
    ('admin', os.path.join(os.path.dirname(django.__file__), 'contrib', 'admin', 'static', 'admin')),
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',

]

#Compressor settings
COMPRESS_URL = STATIC_URL
COMPRESS_ROOT = STATIC_ROOT
STATICFILES_FINDERS += ["compressor.finders.CompressorFinder",]
COMPRESS_OUTPUT_DIR = ""
COMPRESS_CSS_FILTERS = (
    #'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
)
###############################################


###############################################
##Template settings
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#   'django.template.loaders.eggs.Loader',
)
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    TEMPLATES_ROOT.replace('\\', '/'),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    'django.core.context_processors.request',
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "contrib.context_processors.facebook"
)
###############################################


###############################################
##INSTALLED APPS SETTINGS
DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.syndication',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    #'django.contrib.comments',

)

THIRD_PARTY_APPS = (
    #put external 3rd-party installed apps here
    'south',
    #'mailer',
    #'haystack',
    #'facebook',
    #'social_auth',
    #'registration',
    #'imagekit',
    'compressor',
    #'pagination',
    #'facebook_comments',

)

PROJECT_APPS = (
    #put your internal project apps here
    #'app',
    'contrib',
    'contrib.errors',

)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS
###############################################


###############################################
##Email settings::

DEFAULT_FROM_EMAIL = ''
SERVER_EMAIL = ''

##Email Hosting settings (smtp Gmail example)::
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587
EMAIL_USE_TLS = True

#If using django-mailer
if 'mailer' in INSTALLED_APPS:
    EMAIL_BACKEND = 'mailer.backend.DbBackend'
    #what django-mailer will actually use
    MAILER_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    #MAILER_EMAIL_BACKEND = 'django_ses.SESBackend'

#You can also use the Python SMTP debugging server. Run it with:
#python -m smtpd -n -c DebuggingServer localhost:1025
#EMAIL_PORT = 1025
###############################################


###############################################
#EXTRA SETTINGS
#ACCOUNT_ACTIVATION_DAYS = 7 #One-week activation window


#Haystack Settings
#HAYSTACK_SITECONF = 'search_sites'
#HAYSTACK_SEARCH_ENGINE = 'whoosh'
#HAYSTACK_WHOOSH_PATH = os.path.join(APPS_ROOT, 'search/whoosh-index')


#Facebook Settings
#FACEBOOK_APP_ID = os.environ['FACEBOOK_APP_ID']
#FACEBOOK_APP_SECRET = os.environ['FACEBOOK_APP_SECRET']
#FACEBOOK_API_SECRET = os.environ['FACEBOOK_API_SECRET']
#FACEBOOK_SCOPE = 'email,publish_stream'
#FACEBOOK_EXTENDED_PERMISSIONS = [
    #'publish_stream',
    #'email'
#]

AUTHENTICATION_BACKENDS = ('social_auth.backends.facebook.FacebookBackend',
                           'django.contrib.auth.backends.ModelBackend')

#LOGIN_REDIRECT_URL = '/users/'
#LOGOUT_URL = '/users/logout/'
#LOGIN_URL = '/users/login/'
#LOGIN_ERROR_URL = '/users/login-error/'


#SITE_PREFIX = 'http://domain.com.br'
