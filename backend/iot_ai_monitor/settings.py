from pathlib import Path
from decouple import config
from datetime import timedelta

# ==============================================================================
# 1. CORE SETTINGS
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['*']
ROOT_URLCONF = 'iot_ai_monitor.urls'
ASGI_APPLICATION = 'iot_ai_monitor.asgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# 2. APPLICATION DEFINITION
# ==============================================================================
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS = [
    'daphne',
    'channels',
    'rest_framework',
    'rest_framework_api_key',
    'drf_spectacular',
]
LOCAL_APPS = [
    'vision.apps.VisionConfig',
    'authentication.apps.AuthenticationConfig',
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ==============================================================================
# 3. MIDDLEWARE
# ==============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==============================================================================
# 4. TEMPLATES & DATABASE
# ==============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default=5432, cast=int),
    }
}

# ==============================================================================
# 5. AUTHENTICATION & API
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'authentication.authentication.APIKeyAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

API_KEY_CUSTOM_HEADER = "HTTP_X_API_KEY"
API_KEY_MODEL = "authentication.UserAPIKey"

# ==============================================================================
# 6. REAL-TIME (CHANNELS)
# ==============================================================================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(config('REDIS_HOST', default='127.0.0.1'), config('REDIS_PORT', default=6379, cast=int))],
        },
    },
}

# ==============================================================================
# 7. INTERNATIONALIZATION & STATIC/MEDIA FILES
# ==============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==============================================================================
# 8. THIRD-PARTY PACKAGES CONFIGURATION
# ==============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'IoT AI Monitor API',
    'DESCRIPTION': 'API documentation for the smart monitoring project.',
    'VERSION': '1.0.0',
    'AUTH_EXTENSIONS': {
        'APIKeyAuth': 'authentication.authentication.APIKeyAuthenticationScheme',
    },
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX_TRIM': False,
    'SCHEMA_PATH_PREFIX': '/api',
    'COMPONENT_SPLIT_REQUEST': True,
}
# ==============================================================================
# 9. LOGGING
# ==============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
