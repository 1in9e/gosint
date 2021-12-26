#!/usr/bin/env python
# -*- coding: utf-8 -*-
from celery import Celery
import os
from time import time
import json

from libs.process import SubProcessSrc
from urllib.parse import urlparse

FILEPATH = os.path.split(os.path.realpath(__file__))[0]

if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'False':
    broker = os.environ['BROKER']
    backend = os.environ['BACKEND']
    DEBUG = "False"
else:
    DEBUG = "True"
    broker = 'redis://127.0.0.1:6379/0'
    backend = 'redis://127.0.0.1:6379/2'

app = Celery('gosint.jsfinder', broker=broker, backend=backend, )
app.config_from_object('config')


@app.task
def run(target):
    result = []
    res_sub = []    # 子域名结果存放
    work_dir = FILEPATH + '/tools'
    # 生成文件
    target_file = 'url_tmp_{}.txt'.format(time())
    file = open(work_dir + '/' + target_file, 'w');
    for tag in target:
        file.write(tag + '\n');
    file.close();

    out_file_name1 = 'jsfinder_{}.txt'.format(time())   # jsfinder.py
    out_file_name2 = 'httpx_{}.txt'.format(time())      # jsfinder ---> httpx
    out_file_name3 = 'jsf_subdomain_{}.txt'.format(time())      # jsfinder -os 子域名

    # JSFinder 部分 执行命令 python3 JSFinder.py httpx
    if DEBUG == 'True':
        command = ['python3', 'JSFinder.py', '-f', target_file, '-ou', out_file_name1, '-os', out_file_name3]
        command2 = ['./httpx_mac', '-silent', '-l', out_file_name1, '-json', '-o',
                    out_file_name2]
    else:
        command = ['python3', 'JSFinder.py', '-f', target_file, '-ou', out_file_name1]
        # 流量代理至xray进行被动扫描
        command2 = ['./httpx', '-silent', '-l', out_file_name1, '-follow-host-redirects', '-json', '-o', out_file_name2,
                    '-http-proxy', 'http://127.0.0.1:7777']
    try:
        sb = SubProcessSrc(command, cwd=work_dir).run()
        if sb['status'] == 0:
            # 运行成功，读取数据
            sb = SubProcessSrc(command2, cwd=work_dir).run()
            if sb['status'] == 0:
                try:
                    # dic = {}
                    with open('{}/{}'.format(work_dir, out_file_name2), 'r') as f:
                        lines = f.readlines()
                        for line in lines:
                            if json.loads(line)['status-code'] in (200, 206, 401, 403, 500, 503) and \
                                    'image' not in json.loads(line)['content-type'] and \
                                    'javascript' not in json.loads(line)['content-type'] and json.loads(line)\
                                    ['path'][-4:] != '.svg':
                                dic = {}
                                # dic["url"] = json.loads(line)['url']
                                urlres = urlparse(json.loads(line)['url'])
                                dic["host"] = urlres.scheme + "://" + urlres.netloc
                                dic['path'] = json.loads(line)['path']
                                dic['cms'] = ''
                                # httpx 某些情况下无content-length字段
                                try:
                                    dic["content-length"] = json.loads(line)['content-length']
                                except Exception as e:
                                    dic["content-length"] = ''
                                dic["status-code"] = json.loads(line)['status-code']
                                # httpx 某些情况下无title字段
                                try:
                                    dic["title"] = json.loads(line)['title']
                                except Exception as e:
                                    dic["title"] = ''
                                result.append(dic)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)
    try:
        with open('{}/{}'.format(work_dir, out_file_name3), 'r') as f:
            for line in f.readlines():
                res_sub.append(line.strip())
    except Exception as e:
        print(e)
    try:
        os.system('rm -rf {}/{}'.format(work_dir, target_file))
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name1))
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name2))
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name3))
    except Exception as e:
        print(e)

    return {'tool': 'jsfinder', 'result': result, 'result_subdomain': list(set(res_sub))}

if __name__ == '__main__':
    target = [
            'https://www.oppo.com',
            'https://www.ohlinge.cn',
              ]
    print(run(target))
