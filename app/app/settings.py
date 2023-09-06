"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 4.0.9.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os

import firebase_admin
from firebase_admin import credentials

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "changeme")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(int(os.environ.get("DEBUG", 0)))

ALLOWED_HOSTS = []
ALLOWED_HOSTS.extend(
    filter(
        None,
        os.environ.get("ALLOWED_HOSTS", "").split(","),
    )
)


# Application definition

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "core",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "user",
    "corsheaders",
    "post",
    "seller",
    "business",
    "dish",
    "menu",
    "imagekit",
]

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.environ.get("DB_HOST"),
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASS"),
    }
}



firebase_credentials = {
  "type": "service_account",
  "project_id": "foodport-app-8c4ee",
  "private_key_id": "bde816935b1c7416225758dc43fc0e5dec977630",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCRu/hLYYddTC4Y\n2txTcwT7BOhWxYqNHY625v1wNNBp89aZ8VitmqFoVqpw2TEzHFV1NP0/EXaFOX5z\n+Z7eqaXaOaoK4sZMNIpmMoPIsVqHTzZxprfueza0kHy2P2v0+txxjrWddZ9NIiOo\nXh8pr24G/Q3MyMDyX1PJ8IX8ARN03ovc9yzXKreAWucKaOsSiFuYt1xRgMYwzkHk\njzBVyCts98dMPCDm5SsA4FhrbHY7J9vgP6hwRYY4inOlVQN0Gw80nGICxBTsjzLD\nVVHUHS+F+CjW1DKaR9gWIKD78ZasuP8SxouS8+dcXNGyGJE1TpP8Ggi8CPVaA5v+\nur7T0pMpAgMBAAECggEAAcJ6nbO7G130yIlhU6313MS9vB59LSBdkskjPPGbpUve\ncX6/4AjCniyTDkhxFvmRRphciSBq2pz2cUFjBl6XXr/c1RjROtD/mCWlVbez13fA\nuTVBefhe5rs/5kDJyuwkhp0p2ubgBOG+pc/NIdxjwGMvLCPYaz90wYwinLJeoRtH\nfBJ34/hnqaAyjalgla3x9RNt86RW6U4/aFqsAZbNGL1UATdntiIrJkWGe7rkcRBj\n2mQMrUvXI3+GRJT7AemoELNAlmpZ5a0KYtXBpIPPagwD29gjgmtNNyktgqEWku0y\n0U0jGUD7FeBIGd84f+CICzc+rpsCfH3G8zQcYoGwiQKBgQDEp/7gTAgmm5E3N3D4\n6GPpo/SbG7FdIKyjLchDowQOwUYM1TzKHmv+DkLl/qrg03CM2CANyApznbhNEZQM\nAQWtrX3zbJrdYarAcNcnnxh2jYfM6oaMn8pBYi6/O9JeCv5YaIvS3QQIdYs1lveF\nmJ9lsq+7okLCoGYZ1qQTpbqLwwKBgQC9tivbLMqxBMCSG3S9MwdyfQv3NlztKu5G\nhqgu0xItpDlcCn2jEFSHK8POwbdkPx3i8bmtoc8Y24XhGNl4WMXOU1z9ruAA+CY0\nrlJx7/cohJfbbevxf4MZP8mM1soS4oDvLxi7Y09NeoqpbYTHwJVTdrhoG5lqvrTE\nDMlgW8qyowKBgQCxgwdBRcBRwTkKg4P5WiPd4T5JyGyIKJdM0GWmD/74pqNpsA2o\nUF+guxTN8NwkBxfgOrJsXjZ4+FRFVOmzEDUk+aboVQ9RZ/iuruy3ehel48lCQixj\nwVTbQhn6SrBwbTH7cZtNIm2iiR+4puYU9JhlPy77itMCRbED/8ipZ36E6wKBgQCP\n5lHH02b/9RnY+ciIBt/8QMvFvc+o+mp4xoVl1yavxiTYIwD/olBro4/IEfp4qMOT\ntEViZh0/vqwDfSTf+343LdaYeoBhW9knFp9k219/tWu2vt88dLtNeKv6D6aBwpuI\nUhIReZfarjvlnjQcjID4KVJhbaXmaTeWihhp5daPvwKBgQDCzY6bTU8UmVwi+Mc1\n5O+1ICazcInokJuOicphm7zOa3yvVudWoZLAGei7grU/u7pOw/mtr4kYZx31BOUA\nXit4+mB/scA138ZRsJ2t1iJlYm+BUpRlmzsFm4tSNYmlc/B7z94tUTagrujDPPqh\nsBS+GtwxmCLf9njPzfIsqaDPiA==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-dmtwd@foodport-app-8c4ee.iam.gserviceaccount.com",
  "client_id": "108942836846038503404",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-dmtwd%40foodport-app-8c4ee.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(firebase_credentials)
default_app = firebase_admin.initialize_app(cred)

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "https://api.foodport.com.my/static/static/"
MEDIA_URL = "https://api.foodport.com.my/static/media/"

MEDIA_ROOT = "/vol/web/media"
STATIC_ROOT = "/vol/web/static"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "core.User"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
EXPIRATION_TIME = 3600

SPECTACULAR_SETTINGS = {
    "COMPONENT_SPLIT_REQUEST": True,
}
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    "https://app.foodport.com.my",
    "http://localhost:5000",
]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
