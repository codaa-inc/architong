import os
import json
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = os.path.dirname(BASE_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/


# 시크릿 변수 선언
secret_file = os.path.join(BASE_DIR, 'config/keys/secret_key.json')

with open(secret_file) as f:
    info = json.loads(f.read())


def get_info(setting, info=info):
    try:
        return info[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_info("SECRET_KEY")


# Application definition

INSTALLED_APPS = [
    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # application
    'apps.common',
    'apps.calculator',
    'apps.book',
    'apps.forum',

    # third party
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'martor',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ko-KR'

TIME_ZONE = 'Asia/Seoul'

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'common.UserInfo'


"""--------------------------------
---------- 정적파일 관리 ------------
--------------------------------"""

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

#  static file들을 라우팅 시킬 URL
STATIC_URL = '/static/'

#  runserver을 통해서 static file에 접근할 때 이용할 경로
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

#  웹서버와 연동하기 위한 collectstatic 경로
STATIC_ROOT = os.path.join(ROOT_DIR, '.static_root')

"""--------------------------------
-------- 구글 OAuth 연동 -----------
--------------------------------"""

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]

# Google OAuth 2.0
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = get_info("OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = get_info("OAUTH2_SECRET")

# 소셜 로그인 공급자를 Google로 지정
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# URL 맵핑
SITE_ID = 2
SOCIAL_AUTH_URL_NAMESPACE = 'social'

"""--------------------------------
---------- Django Auth  -----------
--------------------------------"""

# 로그인, 로그아웃 성공시 경로
LOGIN__URL = '/accounts/google/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Template에서 Session 사용
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
)

"""---------------------------------
-------- 마크다운 에디터 ------------
---------------------------------"""

# Choices are: "semantic", "bootstrap"
MARTOR_THEME = 'bootstrap'

# Global martor settings
# Input: string boolean, `true/false`
MARTOR_ENABLE_CONFIGS = {
    'emoji': 'true',        # to enable/disable emoji icons.
    'imgur': 'true',        # to enable/disable imgur/custom uploader.
    'mention': 'false',     # to enable/di₩sable mention
    'jquery': 'true',       # to include/revoke jquery (require for admin default django)
    'living': 'false',      # to enable/disable live updates in preview
    'spellcheck': 'false',  # to enable/disable spellcheck in form textareas
    'hljs': 'true',         # to enable/disable hljs highlighting in preview
}

# To show the toolbar buttons
MARTOR_TOOLBAR_BUTTONS = [
    'bold', 'italic', 'horizontal', 'heading', 'pre-code',
    'blockquote', 'unordered-list', 'ordered-list',
    'link', 'image-link', 'image-upload', 'emoji',
    'direct-mention', 'toggle-maximize', 'help'
]

# To setup the martor editor with title label or not (default is False)
MARTOR_ENABLE_LABEL = False

# Imgur API Keys
MARTOR_IMGUR_CLIENT_ID = get_info("MARTOR_IMGUR_CLIENT_ID")
MARTOR_IMGUR_API_KEY = get_info("MARTOR_IMGUR_API_KEY")

# Markdownify
MARTOR_MARKDOWNIFY_FUNCTION = 'martor.utils.markdownify'
MARTOR_MARKDOWNIFY_URL = '/martor/markdownify/'

# Markdown extensions (default)
MARTOR_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.nl2br',
    'markdown.extensions.smarty',
    'markdown.extensions.fenced_code',

    # Custom markdown extensions.
    'martor.extensions.urlize',
    'martor.extensions.del_ins',      # ~~strikethrough~~ and ++underscores++
    'martor.extensions.mention',      # to parse markdown mention
    'martor.extensions.emoji',        # to parse markdown emoji
    'martor.extensions.mdx_video',    # to parse embed/iframe video
    'martor.extensions.escape_html',  # to handle the XSS vulnerabilities
]

# Markdown Extensions Configs
MARTOR_MARKDOWN_EXTENSION_CONFIGS = {}

# Markdown urls
MARTOR_UPLOAD_URL = '/martor/uploader/'
MARTOR_SEARCH_USERS_URL = '/martor/search-user/'

# Markdown Extensions
# MARTOR_MARKDOWN_BASE_EMOJI_URL = 'https://www.webfx.com/tools/emoji-cheat-sheet/graphics/emojis/'     # from webfx
MARTOR_MARKDOWN_BASE_EMOJI_URL = 'https://github.githubassets.com/images/icons/emoji/'                  # default from github
MARTOR_MARKDOWN_BASE_MENTION_URL = 'https://python.web.id/author/'                                      # please change this to your domain

# If you need to use your own themed "bootstrap" or "semantic ui" dependency
# replace the values with the file in your static files dir
MARTOR_ALTERNATIVE_JS_FILE_THEME = "semantic-themed/semantic.min.js"   # default None
MARTOR_ALTERNATIVE_CSS_FILE_THEME = "semantic-themed/semantic.min.css" # default None
MARTOR_ALTERNATIVE_JQUERY_JS_FILE = "jquery/dist/jquery.min.js"        # default None

# not set else csrf will not be sent over ajax calls
CSRF_COOKIE_HTTPONLY = False

