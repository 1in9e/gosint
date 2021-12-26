#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from .models import Target
from django.core.exceptions import ValidationError
from django.utils.html import format_html
import re


class AddTargetForm(forms.ModelForm):
    """
    添加目标form
    """
    target_name = forms.CharField(widget=forms.Textarea,)

    target_name.help_text = format_html('<p style="color: red;">每行一个目标。以.开头的顶级域名会进行域名探测，否则只会对对应的域名进行扫描。如.qq.com才会进行域名探测。<br>  可接收目标资产形如：<br>  .domain.com<br>  sub.domain.com<br>  8.8.8.8<br>  8.8.8.8/24<br>  8.8.8.8-10<br></p>')
    target_name.label = '目标资产'

    class Meta:
        model = Target
        fields = ['project', 'target_name', 'target_description', ]

    def clean_target_name(self):
        targets = self.cleaned_data['target_name']
        targets_set = list(set(targets.splitlines()))
        # DONE: 自动去重
        # DOWN: IP段插入
        for target in targets_set:
            """
            update re: by _lin9e in 2021.9.9
                .qq.com
                www.qq.com
                8.8.8.8
                8.8.8.8/24
                8.8.8.8-10
            """
            if not re.match('^(?=^.{3,255}$)[\.a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+(?:\/\d*)?', target):
                raise ValidationError('请输入正确的域名、IP或IP段！')
        return targets

