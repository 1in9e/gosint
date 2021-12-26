#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery import Celery
import os
import json
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

app = Celery('gosint.nuclei', broker=broker, backend=backend, )
app.config_from_object('config')


@app.task
def run(target):
    work_dir = FILEPATH + '/tools'
    out_file_name = '{}.json'.format(time())

    # 生成文件
    target_file = 'url_tmp_{}.txt'.format(time())
    file = open(work_dir + '/' + target_file, 'w');
    for tag in target:
        file.write(tag + '\n');
    file.close();

    # 执行命令 ./nuclei -target url -silent -json -o filename -config config.yaml
    if DEBUG == 'True':
        # command = ['whoami']
        command = ['./nuclei_mac', '-l', target_file, '-json', '-o', out_file_name, '-config', 'config.yaml']
    else:
        command = ['./nuclei', '-l', target_file, '-json', '-silent', '-o', out_file_name, '-config', 'config.yaml']
    print(command)
    sb = SubProcessSrc(command, cwd=work_dir).run()
    result = []
    if sb['status'] == 0:
        # 运行成功，读取txt数据返回
        with open('{}/{}'.format(work_dir, out_file_name), 'r') as f:
            for line in f.readlines():
                dic = {}
                """
                # 每一行的json格式示例：
                # {"templateID":"apache-version-detect","info":{"name":"Apache Version","author":"philippedelteil","description":"Some Apache servers have the version on the response header. The OpenSSL version can be also obtained","severity":"info"},"type":"http","host":"https://www.ohlinge.cn","matched":"https://www.ohlinge.cn","extracted_results":["Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/5.4.16"],"ip":"14.204.144.151","timestamp":"2021-06-23T17:16:02.454592+08:00"}
                """
                dic['templateID'] = json.loads(line)['templateID']  # template name
                dic['severity'] = json.loads(line)['info']['severity']  # 漏洞级别
                dic['host'] = json.loads(line)['host']   # host url
                dic['matched'] = json.loads(line)['matched']    # 漏洞URL
                dic['detail'] = line.strip()    # 漏洞详情，计划为全json内容
                result.append(dic)
    try:
        os.system('rm -rf {}/{}'.format(work_dir, target_file))
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name))
    except Exception as e:
        print(e)

    return {'tool': 'nuclei', 'result': result}

if __name__ == '__main__':
    target = ['https://www.ohlinge.cn',
              'https://www.jd.com',]
    print(run(target))
