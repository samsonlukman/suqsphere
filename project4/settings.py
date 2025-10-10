"""
Django settings for project4 project.
"""

import os
from celery.schedules import crontab

# --- BASE DIR ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# ⚙️ SECURITY SETTINGS
# ============================================================
SECRET_KEY = '13kl@xtukpwe&xj2xoysxe9_6=tf@f8ewxer5n&ifnd46+6$%8'
DEBUG = False  # 🚀 Set to False in production

ALLOWED_HOSTS = [
    'suqsphere.com', '127.0.0.1', 'www.suqsphere.com', '13.60.34.232', '10.102.181.66',  '192.168.0.202'
]

# ============================================================
# 📦 INSTALLED APPS
# ============================================================
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

# ============================================================
# 🧩 MIDDLEWARE
# ============================================================
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

# ============================================================
# 🌐 REST FRAMEWORK / CORS
# ============================================================
ROOT_URLCONF = 'project4.urls'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny']
}

CSRF_TRUSTED_ORIGINS = [
    'https://suqsphere.com',
    'https://www.suqsphere.com',
    # Note: These values must include the scheme (http:// or https://)
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = ['access-control-allow-origin', 'content-type']
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']

# ============================================================
# 🧱 TEMPLATES
# ============================================================
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

# ============================================================
# ⚙️ APPLICATION ROUTING
# ============================================================
WSGI_APPLICATION = 'project4.wsgi.application'
ASGI_APPLICATION = 'project4.asgi.application'

# ============================================================
# 🗄️ DATABASE CONFIGURATION
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # ❗ Replace with PostgreSQL/MySQL in production if needed
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# ============================================================
# 👥 AUTH CONFIGURATION
# ============================================================
AUTH_USER_MODEL = "network.User"

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================
# 🌍 INTERNATIONALIZATION
# ============================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ============================================================
# 📧 EMAIL CONFIGURATION
# ============================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'lucassamson24@gmail.com'
EMAIL_HOST_PASSWORD = 'ezgokvqbrzfnfbjw'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'lucassamson24@gmail.com'

# ============================================================
# 🖼️ STATIC & MEDIA
# ============================================================
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# ============================================================
# 🚀 Celery Configuration (Production with Redis)
# ============================================================
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# --- Development (use these only for local testing) ---
# CELERY_BROKER_URL = 'memory://'
# CELERY_RESULT_BACKEND = 'cache+memory://'

CELERY_BEAT_SCHEDULE = {
    'send-ai-daily-notifications': {
        'task': 'network.notifications.tasks.send_ai_daily_notifications',
        'schedule': crontab(hour=9, minute=0),  # Runs daily at 9 AM
    },
    "send_market_update_notifications": {
        "task": "network.notifications.tasks.send_market_update_notifications",
        "schedule": crontab(hour=12, minute=0),
    },
}

# ============================================================
# 🔌 Channels / WebSocket Layer (Production with Redis)
# ============================================================
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}


SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# This forces URL generation to use HTTPS
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- Development (InMemory) ---
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels.layers.InMemoryChannelLayer",
#     }
# }

# ============================================================
# 🔒 ADDITIONAL SECURITY SETTINGS (Recommended)
# ============================================================
