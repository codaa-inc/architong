from .base import *

DEBUG = False


ALLOWED_HOSTS = [get_info("ALLOWED_HOSTS"),
                 'codetect.io', 'localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_info("NAME"),
        'USER': get_info("USER"),
        'PASSWORD': get_info("PASSWORD"),
        'HOST': get_info("HOST"),
        'PORT': get_info("PORT"),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
