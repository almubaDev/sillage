import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Usar variables de entorno con valores por defecto solo para configuraciones no sensibles
SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

#ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '.ngrok.io',  # Permite cualquier subdominio de ngrok.io
    '.ngrok-free.app',  # Para las nuevas URLs de ngrok
]



CSRF_TRUSTED_ORIGINS = [
    f"https://{origin}" for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '8bd4-200-104-85-14.ngrok-free.app').split(',')
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'markdownify',
    'pwa',
    
    'users',
    'recomendador',
    'perfumes',
    'administrador',
    'home',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Middleware para internacionalización en posición correcta
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',  # Asegurarse de que este procesador esté presente
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Configuración de logging
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
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'administrador': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

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

# Zona horaria e internacionalización
TIME_ZONE = 'America/Santiago'
USE_TZ = True

LANGUAGE_CODE = 'es'
LANGUAGES = [
    ('es', 'Español'),
    ('en', 'English'),
]

USE_I18N = True
USE_L10N = True

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Archivos estáticos y media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Autenticación
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'users:perfil'
LOGOUT_REDIRECT_URL = 'users:login'
LOGIN_URL = 'users:login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# APIs externas - SIN valores por defecto para credenciales sensibles
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Configuración de PayPal
PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')

if PAYPAL_MODE == 'sandbox':
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_SANDBOX_CLIENT_ID')
    PAYPAL_SECRET = os.getenv('PAYPAL_SANDBOX_SECRET')
    PAYPAL_API_BASE = 'https://api-m.sandbox.paypal.com'
    PAYPAL_WEBHOOK_ID = os.getenv('PAYPAL_SANDBOX_WEBHOOK_ID')
    PAYPAL_PRODUCT_ID = os.getenv('PAYPAL_SANDBOX_PRODUCT_ID')
    PAYPAL_PLAN_ID = os.getenv('PAYPAL_SANDBOX_PLAN_ID')
else:  # 'live'
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_LIVE_CLIENT_ID')
    PAYPAL_SECRET = os.getenv('PAYPAL_LIVE_SECRET')
    PAYPAL_API_BASE = 'https://api-m.paypal.com'
    PAYPAL_WEBHOOK_ID = os.getenv('PAYPAL_LIVE_WEBHOOK_ID')
    PAYPAL_PRODUCT_ID = os.getenv('PAYPAL_LIVE_PRODUCT_ID')
    PAYPAL_PLAN_ID = os.getenv('PAYPAL_LIVE_PLAN_ID')

# Duración de la sesión (30 días en segundos)
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30


# Añadir configuración para PWA
PWA_APP_NAME = 'Sillage'
PWA_APP_DESCRIPTION = "Tu recomendador personal de perfumes"
PWA_APP_THEME_COLOR = '#D4AF37'
PWA_APP_BACKGROUND_COLOR = '#0B0B0B'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_START_URL = '/es/recomendador/' 
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_ICONS = [
    {
        'src': '/static/img/icons/icon-128x128.png',
        'sizes': '128x128'
    },
    {
        'src': '/static/img/icons/icon-144x144.png',
        'sizes': '144x144'
    },
    {
        'src': '/static/img/icons/icon-152x152.png',
        'sizes': '152x152'
    },
    {
        'src': '/static/img/icons/icon-192x192.png',
        'sizes': '192x192'
    },
    {
        'src': '/static/img/icons/icon-256x256.png',
        'sizes': '256x256'
    },
    {
        'src': '/static/img/icons/icon-512x512.png',
        'sizes': '512x512'
    }
]
PWA_APP_ICONS_APPLE = [
    {
        'src': '/static/img/icons/apple-icon-152x152.png',
        'sizes': '152x152'
    },
    {
        'src': '/static/img/icons/apple-icon-180x180.png',
        'sizes': '180x180'
    }
]
PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/img/splash/splash-640x1136.png',
        'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
    }
]
PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'es-ES'
PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'static/js', 'serviceworker.js')