"""
Django settings for project4 project.
"""

import os
from celery.schedules import crontab

# --- BASE DIR ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- SECURITY ---
SECRET_KEY = '13kl@xtukpwe&xj2xoysxe9_6=tf@f8ewxer5n&ifnd46+6$%8'
DEBUG = True

ALLOWED_HOSTS = [
    '10.102.181.66', '127.0.0.1', '127.0.0.1:8000',
    'suqsphere.com', 'www.suqsphere.com', '13.60.34.232'
]

# --- APPS ---
INSTALLED_APPS = [
    'daphne',
    'channels',
    'network',
    'django_celery_results',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- REST / CORS ---
ROOT_URLCONF = 'project4.urls'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny']
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = ['access-control-allow-origin', 'content-type']
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']

# --- TEMPLATES ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'network.custom_context_processors.my_groups_and_joined',
                'network.custom_context_processors.user_connections',
            ],
        },
    },
]

# --- APPS / ROUTING ---
WSGI_APPLICATION = 'project4.wsgi.application'
ASGI_APPLICATION = 'project4.asgi.application'

# --- DATABASE ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# --- AUTH ---
AUTH_USER_MODEL = "network.User"

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- I18N ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# --- EMAIL ---
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'lucassamson24@gmail.com'
EMAIL_HOST_PASSWORD = 'ezgokvqbrzfnfbjw'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'lucassamson24@gmail.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# --- STATIC & MEDIA ---
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# ============================================================
# 🚀 Celery Configuration
# ============================================================

# ✅ DEVELOPMENT (no Redis needed)
# Celery Configuration
CELERY_BROKER_URL = 'django-db://'  # Use database as broker
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_ACKS_LATE = False
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
# In production, you’ll uncomment these 👇
# CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
# CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

CELERY_BEAT_SCHEDULE = {
    'send-ai-daily-notifications': {
        'task': 'network.notifications.tasks.send_ai_daily_notifications',
        'schedule': crontab(hour=9, minute=0),  # 9AM daily
    },
}

# ============================================================
# 🔌 Channels / WebSocket Layer
# ============================================================

# ✅ DEVELOPMENT (InMemory)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# In production, you’ll switch to Redis 👇
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [("127.0.0.1", 6379)],
#         },
#     },
# }
