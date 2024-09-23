"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-c4m5ru74e=0=aeevzty$%@7nqg#(1s75iv_#cpkr5+5upppta='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    '.herokuapp.com',
    'localhost', 
    '127.0.0.1'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework', # 追加
    'app.apps.AppConfig', # 追加
    'corsheaders', # 追加
    'rest_framework_simplejwt.token_blacklist',  # JWTトークンの無効化をサポート
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 追加 (できるだけ上の方に配置)
    'django.middleware.common.CommonMiddleware',  # 追加
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 追加
]

ROOT_URLCONF = 'project.urls'

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

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',#どのDBでもPostgreSQLなら同じ
        'NAME': 'deg7ou4g8mafdu',  # Heroku Postgresで確認したDatabaseの値を入力
        'USER': 'u7s2mnar60k61u',  # Heroku Postgresで確認したUserの値を入力
        'PASSWORD': 'p067094e3e7eb828f33a2d6a48ff2f9e1f21638ab499c557e1c934b5affb9c378',  # Heroku Postgresで確認したPasswordの値を入力
        'HOST': 'cbec45869p4jbu.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com',  # Heroku Postgresで確認したHostの値を入力
        'PORT': '5432',  # どのDBでもPostgreSQLなら同じ
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_ALL_ORIGINS = True

CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # フロントエンドのオリジン
    'https://aichihack-back-153bffff1dd9.herokuapp.com',  # バックエンドのURL（オプション）
]


MEDIA_URL = '/images/'
MEDIA_ROOT = BASE_DIR / 'images'

AUTH_USER_MODEL = 'app.User'  # appはアプリケーション名

# オプション: JWTの有効期限をカスタマイズ
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),  # アクセストークンの有効期限
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),  # リフレッシュトークンの有効期限
    'ROTATE_REFRESH_TOKENS': True,  # リフレッシュ時に新しいリフレッシュトークンを発行する
    'BLACKLIST_AFTER_ROTATION': True,  # リフレッシュ後、古いトークンを無効にする
}

import os
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT認証のみを使用
    ),
}

# 信頼できるオリジンをCSRF対策として追加
CSRF_TRUSTED_ORIGINS = [
    'https://aichihack-back-153bffff1dd9.herokuapp.com',
    'http://localhost:3000',
]

# Whitenoise で提供される静的ファイルに CORS を許可しない
WHITENOISE_ALLOW_ALL_ORIGINS = False