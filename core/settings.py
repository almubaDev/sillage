import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Usar variables de entorno con valores por defecto solo para configuraciones no sensibles
SECRET_KEY = "django-insecure-ed$du#r93c^-pj9l(-lwpr8=(nrsc3y02&0)#3hq8^z67&=hm("

DEBUG = False

#ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'isler.pythonanywhere.com']


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
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'isler$default',
        'USER': 'isler',
        'PASSWORD': 'Anada!312$',  # La contraseña que configuraste
        'HOST': 'isler.mysql.pythonanywhere-services.com',
        'PORT': '',
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
OPENWEATHER_API_KEY="f3df07cd491790df460045d5478882fc"
GEMINI_API_KEY="AIzaSyA8s0lcBuA5FI13sy1xZP2iGHhQ2AtiMtQ"
GOOGLE_MAPS_API_KEY="AIzaSyBYW7kK_nRl4IHm8P5_MPqPDVPbMl7J-n0"

#Flow config
FLOW_API_KEY="23F00F2E-779B-4C7B-9AD0-64E551L7C9FC"
FLOW_SECRET_KEY="b15579cf8b18bf709eb98b692845112a357208ac"
FLOW_API_URL="https://sandbox.flow.cl/api"  # URL para pruebas
FLOW_SANDBOX=True





# # Configuración de PayPal
# PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')

# if PAYPAL_MODE == 'sandbox':
#     PAYPAL_CLIENT_ID = os.getenv('PAYPAL_SANDBOX_CLIENT_ID')
#     PAYPAL_SECRET = os.getenv('PAYPAL_SANDBOX_SECRET')
#     PAYPAL_API_BASE = 'https://api-m.sandbox.paypal.com'
#     PAYPAL_WEBHOOK_ID = os.getenv('PAYPAL_SANDBOX_WEBHOOK_ID')
#     PAYPAL_PRODUCT_ID = os.getenv('PAYPAL_SANDBOX_PRODUCT_ID')
#     PAYPAL_PLAN_ID = os.getenv('PAYPAL_SANDBOX_PLAN_ID')
# else:  # 'live'
#     PAYPAL_CLIENT_ID = os.getenv('PAYPAL_LIVE_CLIENT_ID')
#     PAYPAL_SECRET = os.getenv('PAYPAL_LIVE_SECRET')
#     PAYPAL_API_BASE = 'https://api-m.paypal.com'
#     PAYPAL_WEBHOOK_ID = os.getenv('PAYPAL_LIVE_WEBHOOK_ID')
#     PAYPAL_PRODUCT_ID = os.getenv('PAYPAL_LIVE_PRODUCT_ID')
#     PAYPAL_PLAN_ID = os.getenv('PAYPAL_LIVE_PLAN_ID')

