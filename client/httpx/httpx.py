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

app = Celery('gosint.httpx', broker=broker, backend=backend, )
app.config_from_object('config')


@app.task
def run(target):
    #生成文件
    target_file = 'httpxtmp_{}.txt'.format(time())
    file = open(FILEPATH + '/tools/' + target_file, 'w');
    for tag in target:
        file.write(tag + '\n');
    file.close();

    work_dir = FILEPATH + '/tools'
    out_file_name = '{}_{}.json'.format(target_file, time())
    # 执行命令 ./httpx_mac -l vivo.com.txt -cdn -json -follow-host-redirects -o 111.json
    if DEBUG == 'True':
        # command = ['whoami']
        #./httpx_mac -l vivo.com.txt -cdn -json -follow-host-redirects -o 111.json
        command = ['./httpx_mac', '-silent', '-l', target_file, '-json', '-o', out_file_name]
    else:
        command = ['./httpx', '-silent', '-l', target_file, '-json', '-o', out_file_name]
    result = []
    #整体抛出异常，以防httpx自身报错
    try:
        sb = SubProcessSrc(command, cwd=work_dir).run()
        if sb['status'] == 0:
            # 运行成功，读取json数据返回
            with open('{}/{}'.format(work_dir, out_file_name), 'r') as f:
                url = f.readlines()
                for line in url:
                    #print(line)
                    dic = {}
                    dic["url"] = json.loads(line)['url']
                    # httpx 某些情况下无content-length字段
                    try:
                        dic["content-length"] = json.loads(line)['content-length']
                    except:
                        dic["content-length"] = 0
                    dic["status-code"] = json.loads(line)['status-code']
                    # httpx 某些情况下无title字段
                    try:
                        dic["title"] = json.loads(line)['title']
                    except:
                        dic["title"] = ''
                    try:
                        dic['webserver'] = json.loads(line)['webserver']
                    except:
                        dic['webserver'] = ''
                    # dic["cdn"] = json.loads(line)['cdn']
                    # print(dic)
                    if dic["status-code"] in (101, 200, 204, 206, 301, 302, 308, 401, 403, 500, 502):
                        result.append(dic)
    except Exception as e:
        print(e)
    # 当httpx出错，导致生成不了文件时，抛出异常
    try:
        os.system('rm -rf {}/{}'.format(work_dir, target_file))
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name))
    except:
        pass
    return {'tool': 'httpx', 'result': result}

if __name__ == '__main__':
    testlist = [
        "hunachaco.vivo.com",
        "stat.vivo.com",
        "webcloud.vivo.com",
        "auth.vivo.com",
    ]
    list2 = ['www.ohlinge.cn']
    print(run(list2))
