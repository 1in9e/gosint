#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ansrej*g9t!*0$g40d($9^^#i_$j)^*e2-5bvgi5+y43q@msvh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'simplepro',
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.targetApp.apps.TargetappConfig',
    'apps.scans.apps.ScansConfig',
    'apps.scanEngine.apps.ScanengineConfig',
    'apps.assets.apps.AssetsConfig',
    'apps.dashboard.apps.DashboardConfig',
    'celery',
    'import_export',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # simple ui pro middleware
    'simplepro.middlewares.SimpleMiddleware'
]

ROOT_URLCONF = 'gosint.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR + '/templates']
        ,
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

WSGI_APPLICATION = 'gosint.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gosint',
        'USER': 'gosint',
        'PASSWORD': 'gosint',
        'HOST': 'db',
        'PORT': '3306',
        'CONN_MAX_AGE': 60,
        "OPTIONS": {"init_command": "SET default_storage_engine=INNODB;"}
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static')
# ]


X_FRAME_OPTIONS = 'SAMEORIGIN'


'''
CELERY settings
'''
CELERY_BROKER_URL = 'amqp://gosintuser:gosintpass@rabbitmq:5672/gosint'
CELERY_RESULT_BACKEND = 'redis://:gosintpass@redis:6379/2'
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = 'Asia/Shanghai'

"""
Simple UI settings
"""
SIMPLEUI_HOME_TITLE = 'Gosint'
# SIMPLEUI_LOGO = 'https://xxx/images/avatar.png'
SIMPLEUI_HOME_ICON = 'fa fa-user'
SIMPLEUI_DEFAULT_THEME = 'Simpleui-x.css'
SIMPLEUI_ANALYSIS = False         # 不提交分析
SIMPLEUI_STATIC_OFFLINE = True    # simpleui 是否以脱机模式加载静态资源
SIMPLEPRO_INFO = False      # 不显示激活信息
SIMPLEPRO_CHART_DISPLAY = True      # 配置Simple Pro是否显示首页的图标，默认为True，显示图表，False不显示
SIMPLEUI_HOME_ACTION = True
# SIMPLEUI_DEFAULT_ICON = False   # 不使用默认图标
SIMPLEUI_CONFIG = {
    'system_keep': True,
    'menu_display': ['项目管理', '扫描管理', '资产管理', '漏洞管理', '扫描引擎', '日志管理', '认证和授权'],      # 开启排序和过滤功能, 不填此字段为默认排序和全部显示, 空列表[] 为全部不显示.
    'menus': [{
        'app': 'targetApp',
        'name': '项目管理',
        'icon': 'fab fa-battle-net',
        'models': [{
            'name': '项目管理',
            'url': 'targetApp/project/',
            'icon': 'fas fa-cookie-bite'
            }, {
            'name': '目标管理',
            'url': 'targetApp/target/',
            'icon': 'fas fa-glasses'
            }]
        },
        {
            'name': '扫描管理',
            'url': 'scans/scans/',
            'icon': 'fas fa-anchor'
        },
        {
            'name': '扫描引擎',
            'url': 'scanEngine/enginetype/',
            # 'icon': 'fas fa-anchor'
            'icon': 'fab fa-d-and-d'
        }, {
        'app': 'assets',
        'name': '资产管理',
        'icon': 'fas fa-feather',
        'models': [{
            'name': '子域名',
            'url': 'assets/subdomain/',
            'icon': 'fab fa-apple'
        },{
            'name': 'IP资产',
            'url': 'assets/ip/',
            'icon': 'fas fa-skull-crossbones'
        },{
            'name': 'C段情报',
            'url': 'assets/ipc/',
            'icon': 'fas fa-skull-crossbones'
        },{
            'name': '端口服务',
            'url': 'assets/port/',
            'icon': 'fab fa-affiliatetheme'
        },{
            'name': 'web应用',
            'url': 'assets/webapp/',
            'icon': 'fas fa-dove'
        }, {
            'name': '黑名单资产',
            'url': 'assets/blockassets/',
            'icon': 'fas fa-times-circle'
            }
        ]
    }, {
        'app': 'vulnerability',
        'name': '漏洞管理',
        'icon': 'fas fa-user-secret',
        'models': [
            {
            'name': '文件指纹',
            'url': 'assets/fileleak/',
            'icon': 'fas fa-cat'
            }, {
            'name': 'URL爬虫',
            'url': 'assets/crawlerurl/',
            'icon': 'fas fa-spider'
            }, {
            'name': '主动扫描',
            'url': 'assets/nuclei/',
            'icon': 'fas fa-dragon'
            }, {
            'name': '被动扫描',
            'url': 'assets/rad2xray/',
            'icon': 'fas fa-frog'
            }
            ]
        },
        {
        'app': 'log',
        'name': '日志管理',
        'icon': 'fab fa-btc',
        'models': [
            {
            'name': '日志记录',
            'url': 'admin/logentry/',
            'icon': 'fas fa-mitten'
            },{
            'name': 'Celery监控',
            'url': 'http://127.0.0.1:5555/goflower/',
            'icon': 'fas fa-skiing'
            }]
        }
    ]
}

"""
EMAIL settings
"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_USE_TLS = True
# EMAIL_PORT = 994
EMAIL_HOST_USER = 'xxx@163.com'
EMAIL_HOST_PASSWORD = 'xxx'
EMAIL_SUBJECT_PREFIX = 'gosint'
EMAIL_RECEIVE_LIST = ['xxx@qq.com', ]

"""
QIYE WECHAT settings
企业微信推送设置
"""
WECHAT_SEND = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key='
