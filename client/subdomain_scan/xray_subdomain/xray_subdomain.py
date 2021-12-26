#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/17 10:28
# @Author  : _lin9e
from celery import Celery
import os
from time import time

from libs.process import SubProcessSrc

FILEPATH = os.path.split(os.path.realpath(__file__))[0]

if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'False':
    broker = os.environ['BROKER']
    backend = os.environ['BACKEND']
    DEBUG = "False"
else:
    DEBUG = "True"
    broker = 'redis://127.0.0.1:6379/0'
    backend = 'redis://127.0.0.1:6379/2'

app = Celery('gosint.xray_subdomain', broker=broker, backend=backend, )
app.config_from_object('config')


@app.task
def run(domain):
    work_dir = FILEPATH + '/tools'
    out_file_name = '{}_{}.txt'.format(domain, time())
    # 执行命令 ./xray subdomain --target example.cn --text-output example.cn.txt
    if DEBUG == 'True':
        # command = ['whoami']
        command = ['./xray_mac', 'subdomain', '--target', domain, '--text-output', out_file_name]
    else:
        command = ['./xray', 'subdomain', '--target', domain, '--text-output', out_file_name]
    print(command)
    sb = SubProcessSrc(command, cwd=work_dir).run()
    result = []
    if sb['status'] == 0:
        # 运行成功，读取json数据返回
        try:
            with open('{}/{}'.format(work_dir, out_file_name), 'r') as f:
                subdomains = f.readlines()
                for line in subdomains:
                    sub = line.split(",")[0].strip()
                    # print(sub)
                    result.append(sub.strip())
        except Exception as e:
            print(e)
    try:
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name))
    except Exception as e:
        print(e)
    return {'tool': 'xray_subdomain', 'result': result}


if __name__ == '__main__':
    run('ohlinge.cn')
    # run('nearme.com')