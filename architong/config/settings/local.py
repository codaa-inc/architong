from .base import *

DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'architong',
        'USER': 'admin',
        'PASSWORD': get_info("PASSWORD"),
        'HOST': 'localhost',
        'PORT': '3306'
    }
}

