#!/usr/bin/env python
# -*- coding: utf-8 -*-
# _lin9e
# 2021.8.19

from celery import Celery
import os
import json
from time import time
from time import sleep

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

app = Celery('gosint.rad2xray', broker=broker, backend=backend, )
app.config_from_object('config')

@app.task
def run(targets):
    result = []

    for target in targets:
        work_dir = FILEPATH + '/tools'
        out_file_name = '{}.json'.format(time())
        # 执行命令 ./rad -t http://testphp.vulnweb.com -http-proxy 127.0.0.1:7777 --no-banner
        # command2为rad结束后清除多余浏览器进程, macos 与 python-alpine
        if DEBUG == 'True':
            command = ['./rad_darwin_amd64', "-t", target, "--no-banner", "--json-output", out_file_name]
            command2 = "ps aux | awk '/chrome/ { print $2 } ' | xargs kill -9"
        else:
            command = ["./rad", "-t", target, "-http-proxy", "127.0.0.1:7777", "--no-banner", "--json-output",
                       out_file_name]
            command2 = "ps aux | awk '/chrome/ { print $1 } ' | xargs kill -9"
        print(command)
        sb = SubProcessSrc(command, cwd=work_dir).run()
        if sb['status'] == 0:
            # # 清除多余Chrome进程
            try:
                sleep(3)
                os.system(command2)
            except Exception as e:
                print(e)
            try:
                with open('{}/{}'.format(work_dir, out_file_name), 'r') as f:
                # with open("tools/1629372486.905469.json", 'r') as f:
                    for line in json.loads(f.read()):
                        dic = {}
                        dic['Method'] = line['Method']
                        dic['URL'] = line['URL']
                        dic['b64_body'] = line['b64_body'] if dic['Method'] == "POST" else ''
                        dic['Header'] = line['Header']
                        result.append(dic)
                        # print(dic)
            except Exception as e:
                print(e)
        try:
            os.system('rm -rf {}/{}'.format(work_dir, out_file_name))
        except Exception as e:
            print(e)

    return {'tool': 'rad2xray', 'result': result}

if __name__ == '__main__':
    target = ['http://testphp.vulnweb.com', ]
    print(run(target))
