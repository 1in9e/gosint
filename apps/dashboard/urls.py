#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/2 3:15 下午
# @Author  : _lin9e
# @File    : urls.py

from django.urls import path
from . import views

urlpatterns = [
     path('webhook_a5c3d08371aec44c/', views.XrayWebhookView.as_view()),
]
