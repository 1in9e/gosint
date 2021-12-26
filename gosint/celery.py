#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from celery import Celery
from django.conf import settings

if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'false':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gosint.setting-prod')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gosint.settings')

app = Celery('gosint')

app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks()

