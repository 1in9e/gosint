#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery import Celery
import os
from time import time
import json

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

app = Celery('gosint.subfinder', broker=broker, backend=backend, )
app.config_from_object('config')


@app.task
def run(domain):
    work_dir = FILEPATH + '/tools'
    out_file_name = '{}_{}.json'.format(domain, time())
    # 执行命令 ./subfinder_mac -d example.com -json
    if DEBUG == 'True':
        # command = ['whoami']
        # command = ['./subfinder_mac', '-silent', '-d', domain, '-oJ', '-o', out_file_name]
        command = ['./subfinder_mac', '-silent', '-config', 'config.yaml', '-d', domain, '-all', '-t', '200',
                   '-oJ', '-nW', '-o', out_file_name]
        print(command)
    else:
        command = ['./subfinder', '-silent', '-config', 'config.yaml', '-d', domain, '-all', '-nW', '-t', '500',
                   '-oJ', '-o', out_file_name]
    sb = SubProcessSrc(command, cwd=work_dir).run()
    result = []
    if sb['status'] == 0:
        # 运行成功，读取json数据返回
        with open('{}/{}'.format(work_dir, out_file_name), 'r') as f:
            subdomains = f.readlines()
            for line in subdomains:
                # print(line)
                result.append(json.loads(line)['host'].strip())
    try:
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name))
    except Exception as e:
        print(e)
    return {'tool': 'subfinder', 'result': result}


if __name__ == '__main__':
    print(run('myoas.com'))
