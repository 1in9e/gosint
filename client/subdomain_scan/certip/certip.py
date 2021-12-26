#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/30 14:38
# @Author  : _lin9e
# @File    : cert_ip.py

from celery import Celery
import os
import yaml
import aiohttp
import asyncio
import base64
from time import time, sleep
import json

FILEPATH = os.path.split(os.path.realpath(__file__))[0]

if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'False':
    broker = os.environ['BROKER']
    backend = os.environ['BACKEND']
    DEBUG = "False"
else:
    DEBUG = "True"
    broker = 'redis://127.0.0.1:6379/0'
    backend = 'redis://127.0.0.1:6379/2'

app = Celery('gosint.certip', broker=broker, backend=backend, )
app.config_from_object('config')

FILEPATH = os.path.split(os.path.realpath(__file__))[0]
# get fofa email key
def get_fofa_conf():
    with open(os.path.join(FILEPATH, '../../config.yaml')) as f:
        y = yaml.load(f, Loader=yaml.SafeLoader)
    fofa_email = y['FOFA_EMAIL']
    fofa_key = y['FOFA_KEY']
    return fofa_email, fofa_key


async def Search_Keywords(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            jsonhtml = json.loads(html)
    return jsonhtml

async def CheckKey(email, key):
    print("check fofa key.....")
    url = f"https://fofa.so/api/v1/info/my?email={email}&key={key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            if "fofa_server" not in html:
                print("fofa key error,please check your key")
                return False
            else:
                print("fofa key is true")
                return True

def certip_fofa(email, key, file):
    FOFA_EMAIL = email
    FOFA_KEY = key
    loop = asyncio.get_event_loop()
    task = loop.create_task(CheckKey(FOFA_EMAIL, FOFA_KEY))
    loop.run_until_complete(task)
    # print(task.result())
    if task.result() and file:
        with open(file) as f:
            result = []
            for i in f.readlines():
                i = i.strip()
                search_keywords = "cert.subject="+str(i)
                print(f"fofa查询语法: {search_keywords}")
                search_keyword = base64.b64encode(search_keywords.encode()).decode()
                url = f"https://fofa.so/api/v1/search/all?email={FOFA_EMAIL}&key={FOFA_KEY}&qbase64={search_keyword}&size=10000&fields=ip"
                # print(url)
                loop = asyncio.get_event_loop()
                task = loop.create_task(Search_Keywords(url))
                loop.run_until_complete(task)
                result.append(task.result())
            return result
    else:
        return ''

@app.task
def run(target):
    # 生成文件
    target_file = 'fofa_result_tmp_{}.txt'.format(time())
    file = open(FILEPATH + '/' + target_file, 'w');
    for tag in target:
        file.write(tag + '\n');
    file.close();

    email, key = get_fofa_conf()
    result = []
    try:
        res = certip_fofa(email, key, target_file)
        for jsonhtml in res:
            htmlsize = jsonhtml['size']
            htmlresults = jsonhtml['results']
            for i in range(0, htmlsize):
                dic = {}
                dic["ip"] = htmlresults[i]
                result.append(dic)
    except Exception as e:
        print(e)
    # 删除产生的临时文件
    try:
        os.system('rm -rf {}/{}'.format(FILEPATH, target_file))
    except:
        pass
    # fofa api接口请求过快导致查询结果为空
    sleep(1)

    return {'tool': 'certip', 'result': result}


if __name__ == '__main__':
    list1 = [
        "oppo.com",
    ]
    print(run(list1))
