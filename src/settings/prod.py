from base import *


#redefinition of debug settings from base
DEBUG = False
TEMPLATE_DEBUG = False


###############################################
##Production DB
#Simple PostgreSQL + pgBouncer example::
DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql_psycopg2',
       'NAME': 'db',
       'USER': 'db-user',
       'PASSWORD': '',
       'HOST': '',
       'PORT': '',
   }
}
###############################################


###############################################
##Cache settings
#Simple Memcache example::
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': ['127.0.0.1:11211',],
        'KEY_PREFIX': PROJECT_NAME,
    }
}
CACHE_MIDDLEWARE_SECONDS = 300
###############################################

###############################################
##Cache settings
#Haystack: Solr in production
#HAYSTACK_SEARCH_ENGINE = 'solr'
#HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr'
###############################################

###############################################
##INSTALLED APPS settings
PROD_APPS = (
    'gunicorn',
    'storages',

)
INSTALLED_APPS += PROD_APPS
###############################################


###############################################
##Logging settings
# See http://docs.djangoproject.com/en/dev/topics/logging for more details
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
###############################################


###############################################
##STATIC/MEDIA assets settings

# AWS S3 needs authorization
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

#Static settings
STATIC_URL = 'http://ces27.s3-sa-east-1.amazonaws.com/'

#Media (user-uploaded content) settings (S3)
MEDIA_URL = 'http://ces27.s3-sa-east-1.amazonaws.com/'
AWS_STORAGE_BUCKET_NAME = 'ces27'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

#ImageKit configs
IMAGEKIT_DEFAULT_IMAGE_CACHE_BACKEND = 'imagekit.imagecache.NonValidatingImageCacheBackend'


#Compressor settings
COMPRESS_URL = STATIC_URL
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_OFFLINE = True
###############################################


###############################################
#EXTRA SETTINGS

#Sessions settings
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
#SESSION_COOKIE_DOMAIN = '.domain.com.br'
FORCE_WWW = False

#Bazooka caching approach: Cache the entire site.
MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware', #Always first
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware', #Always last
)
###############################################
