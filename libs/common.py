#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/12 8:17 下午
# @Author  : _lin9e
# @File    : common.py

from django.conf import settings
from django.core.mail import send_mail
import requests, json

def send_to_company(title, content):
    """
    # 企业微信推送接口
    :param title:
    :param content:
    :return:
    """
    r = requests.post(settings.WECHAT_SEND, json={'msgtype': 'markdown',
                                                  'markdown': {
                                                    'content': '# {title} \n '
                                                               '{content}'.format(title=title, content=content)
                                                  },
                                                  })
    if r.json()['errcode'] == 0:
        print('企业微信推送成功: {}'.format(r.json()['errmsg']))
    else:
        print(r.json()['errmsg'])


def send_to_mail(title, content=''):
    """
    # 邮箱推送接口
    :param title:
    :param content:
    :return:
    """
    try:
        send_mail(title, content, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVE_LIST, fail_silently=False, )
        print('邮箱推送成功')
    except Exception as e:
        print(e)

def get_domain_icp(domain):
    try:
        r = requests.get(url='https://api.vvhan.com/api/icp?url=' + str(domain.strip()))
        js = json.loads(r.text)
        icp = js['info']['icp']
        info = icp if '-' not in icp else icp.split('-')[0]
    except Exception as e:
        print(e)
        info = ''
    return info
