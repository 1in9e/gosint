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

app = Celery('gosint.ksubdomain', broker=broker, backend=backend, )
app.config_from_object('config')


@app.task
def run(domain):
    work_dir = FILEPATH + '/tools'
    out_file_name = '{}_{}.txt'.format(domain, time())
    # 执行命令 ./ksubdomain -d baidu.com -l 3 -skip-wild -o baidu.com.txt -silent
    if DEBUG == 'True':
        # command = ['whoami']
        command = ['./ksubdomain_mac', '-d', domain, '-skip-wild', '-silent', '-o', out_file_name]
    else:
        command = ['./ksubdomain', '-d', domain, '-skip-wild', '-silent', '-o', out_file_name]
    print(command)
    try:
        sb = SubProcessSrc(command, cwd=work_dir).run()
        result = []
        if sb['status'] == 0:
            # 运行成功，读取txt数据返回
            with open('{}/{}'.format(work_dir, out_file_name), 'r') as f:
                subdomains = f.readlines()
                for line in subdomains:
                    # print(line)
                    result.append(line.strip())
            os.system('rm -rf {}/{}'.format(work_dir, out_file_name))
    except Exception as e:
        print(e)
    return {'tool': 'ksubdomain', 'result': result}


if __name__ == '__main__':
    run('ohlinge.cn')
