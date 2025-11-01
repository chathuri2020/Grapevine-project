from pathlib import Path
import os

from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = os.path.join(BASE_DIR.parent, '.env')
load_dotenv()  #
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

#ALLOWED_HOSTS = ['https://grapevine.bornbee.com/']

ALLOWED_HOSTS = ['127.0.0.1', 'localhost','0.0.0.0', '9e2208fe0523.ngrok-free.app']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # External Apps
    'users',
    'gradio_dashboard',
  

    # Third Party Apps
    'crispy_forms',
    'crispy_bootstrap5',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', #add the fastapi connection between gradio and djngo
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_management.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'django_management.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

""" DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vitisai',
        'USER': 'root', #grapevinehostcp
        'PASSWORD': 'root', #Vitis@123
        'HOST': 'localhost',
        'PORT': '3306',
        #User “grapevinehostcp_grapevinehostcp” was added to the database “grapevinehostcp_vitisai”.

    }
} """


# Detect CapRover environment
if os.getenv("CAPROVER_APP_ID"):
    # CapRover provides DB credentials automatically
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('MYSQL_DATABASE'),
            'USER': os.getenv('MYSQL_USER'),
            'PASSWORD': os.getenv('MYSQL_PASSWORD'),
            'HOST': os.getenv('MYSQL_HOST'),
            'PORT': os.getenv('MYSQL_PORT', '3306'),
        }
    }
else:
    # Local Docker Compose or local dev
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('MYSQL_DATABASE', 'vitisai'),
            'USER': os.getenv('MYSQL_USER', 'root'),
            'PASSWORD': os.getenv('MYSQL_PASSWORD', 'root'),
            'HOST': os.getenv('MYSQL_HOST', 'db'),
            'PORT': os.getenv('MYSQL_PORT', '3306'),
        }
    }




# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Media Files Settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Settings
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Authentication User Model Settings
AUTH_USER_MODEL = 'users.MyUser'

# Login Settings
LOGIN_URL = 'user_app:login'
LOGIN_REDIRECT_URL = 'user_app:home'
X_FRAME_OPTIONS = 'SAMEORIGIN'
CORS_ALLOW_ALL_ORIGINS = True #conect with fastapi

# Alternatively, specify the exact domain/port of your FastAPI/Gradio server:
# CORS_ALLOWED_ORIGINS = [
#     "http://127.0.0.1:8001",
#     "http://localhost:8001",
# ]