from os import path

### Application settings

BASE_DIR = path.dirname(path.dirname(path.dirname(__file__)))

DEBUG = TEMPLATE_DEBUG = True

INTERNAL_IPS = ('127.0.0.1', )

ADMINS = (
    ('Local Admin', 'root@localhost'),
)

MANAGERS = ADMINS

SECRET_KEY = 'PLEASE-OVERRIDE-IN-LOCAL-SETTINGS'

ROOT_URLCONF = 'gallery.urls'

WSGI_APPLICATION = 'gallery.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'apps.accounts',
    'apps.photos',
    'apps.stream',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'gallery.assets.CompileAssetsMiddleware',
)

### Database settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(BASE_DIR, 'database.sqlite3')
    }
}

### Localization settings

USE_TZ = True
TIME_ZONE = 'America/New_York'

LANGUAGE_CODE = 'en-us'
USE_I18N = False
USE_L10N = False

LOCALE_PATHS = (
    path.join(BASE_DIR, 'gallery', 'locale'),
)

### Session settings

SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds

### Authentication settings

LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'accounts:login'
LOGOUT_URL = 'accounts:logout'

### Template settings

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

TEMPLATE_DIRS = (
    path.join(BASE_DIR, 'gallery', 'templates'),
)

### Static and media settings

STATICFILES_DIRS = (
    path.join(BASE_DIR, 'gallery', 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

MEDIA_ROOT = path.join(BASE_DIR, 'public', 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = path.join(BASE_DIR, 'public', 'static')
STATIC_URL = '/static/'

STATIC_BASE_DIR = path.join(BASE_DIR, 'gallery', 'static')

CSS_FILES = {
    path.join(STATIC_BASE_DIR, 'application.css'): (
        path.join(STATIC_BASE_DIR, 'css/reset.css'),
        path.join(STATIC_BASE_DIR, 'css/fonts.css'),
        path.join(STATIC_BASE_DIR, 'css/base.css'),
        path.join(STATIC_BASE_DIR, 'chosen-1.4.2/chosen.css'),
    )
}

JS_FILES = {
    path.join(STATIC_BASE_DIR, 'application.js'): (
        path.join(STATIC_BASE_DIR, 'js/jquery-2.1.4.js'),
        path.join(STATIC_BASE_DIR, 'js/base.js'),
        path.join(STATIC_BASE_DIR, 'chosen-1.4.2/chosen.jquery.js'),
    )
}

### Project specific settings

ALLOWED_EXTENSIONS = 'zip bmp raw jpg jpeg png gif tiff'.split()

AUTH_CODE_USER = 'auth-code-user'
AUTH_CODE_ADMIN = 'auth-code-admin'
AUTH_CODE_ADMIN_GROUP = 'Admin Group'

PHOTOS_PER_PAGE = 50
