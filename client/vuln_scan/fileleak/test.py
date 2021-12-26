#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/16 2:48 下午
# @Author  : _lin9e
# @File    : test.py
from urllib.parse import urlparse
# 运行成功，读取json数据返回
result = []
with open('tools/succ.txt', 'r') as f:
    path = f.readlines()
    for line in path:
        try:
            dic = {}
            url = line.split(']')[-1].split('\n')[0]
            urlres = urlparse(url)
            dic["host"] = urlres.scheme + "://" + urlres.netloc
            dic["path"] = urlres.path
            dic["content-length"] = line.split('[')[-1].split(']')[0]
            dic["status-code"] = line.split('[')[1].split(']')[0]
            dic["title"] = line.split('[')[2].split(']')[0]
            result.append(dic)
        except Exception as e:
            print(e)

    print(result)