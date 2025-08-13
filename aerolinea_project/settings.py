"""
Django settings for aerolinea_project project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Configuración para Render
if os.getenv('RENDER'):
    DEBUG = False
    ALLOWED_HOSTS = [
        os.getenv('RENDER_EXTERNAL_HOSTNAME', 'rutaceleste.onrender.com'),
        'rutaceleste.onrender.com',
        'localhost',
        '127.0.0.1'
    ]
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
    'core',
    'vuelos',
    'pasajeros',
    'reservas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
]

# WhiteNoise para archivos estáticos en producción
if os.getenv('RENDER'):
    MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')

MIDDLEWARE.extend([
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Para internacionalización
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])

ROOT_URLCONF = 'aerolinea_project.urls'

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
                'django.template.context_processors.i18n',  # Para internacionalización
            ],
        },
    },
]

WSGI_APPLICATION = 'aerolinea_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# Configuración de idiomas
LANGUAGES = [
    ('es', 'Español'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Crear directorio static si no existe
STATIC_DIR = BASE_DIR / 'static'
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(exist_ok=True)

STATICFILES_DIRS = [STATIC_DIR]

# Configuración para producción
if os.getenv('RENDER'):
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# 📧 CONFIGURACIÓN DE EMAIL CON MAILTRAP
# Para desarrollo (Mailtrap Sandbox) - TUS CREDENCIALES REALES
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
    EMAIL_PORT = 2525
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'a2615db73a90f0'  # Tu username real
    EMAIL_HOST_PASSWORD = 'b56dbe98f6e2aa'  # Tu password real
    DEFAULT_FROM_EMAIL = 'noreply@rutaceleste.onrender.com'
else:
    # Para producción (Mailtrap API/SMTP)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'live.smtp.mailtrap.io'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv('MAILTRAP_API_USER', 'api')
    EMAIL_HOST_PASSWORD = os.getenv('MAILTRAP_API_TOKEN', 'tu_api_token')
    DEFAULT_FROM_EMAIL = 'noreply@rutaceleste.onrender.com'
