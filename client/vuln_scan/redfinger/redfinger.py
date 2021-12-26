#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery import Celery
import os
import json
from time import time

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

app = Celery('gosint.redfinger', broker=broker, backend=backend, )
app.config_from_object('config')


@app.task
def run(target):
    work_dir = FILEPATH + '/tools'
    templates_dir = work_dir + '/redfinger-templates'
    out_file_name = '{}.json'.format(time())

    # 生成文件
    target_file = 'url_tmp_{}.txt'.format(time())
    file = open(work_dir + '/' + target_file, 'w');
    for tag in target:
        file.write(tag + '\n');
    file.close();
    # 执行命令 ./redfinger -target url -silent -json -o filename -config config.yaml
    if DEBUG == 'True':
        # command = ['whoami']
        command = ['./Ehole-darwin', '-l', target_file, '-json', out_file_name]
    else:
        command = ['./Ehole', '-l', target_file, '-json', out_file_name]
    print(command)
    sb = SubProcessSrc(command, cwd=work_dir).run()
    result = []
    if sb['status'] == 0:
        # 运行成功，读取txt数据返回
        with open('{}/{}'.format(work_dir, out_file_name), 'r') as f:
            for line in f.readlines():
                try:
                    if json.loads(line)['cms'] == None:
                        continue
                    dic = {}
                    """
                    # 每一行的json格式示例：
                    # {"url":"https://www.ohlinge.cn","cms":["Typecho"],"server":"Apache/2.4.6 (CentOS) OpenSSL/1.0.2k-fips PHP/5.4.16","statuscode":200,"length":44129,"title":"0h1in9e' s Blog | 林歌博客"}
                    """
                    urlres = urlparse(json.loads(line)['url'])
                    dic["host"] = urlres.scheme + "://" + urlres.netloc
                    dic['path'] = ''
                    # dic['url'] = json.loads(line)['url']
                    dic['cms'] = json.loads(line)['cms']
                    dic['title'] = json.loads(line)['title']
                    dic['content-length'] = json.loads(line)['length']
                    dic['status-code'] = json.loads(line)['statuscode']
                    result.append(dic)
                except Exception as e:
                    print(e)
    try:
        os.system('rm -rf {}/{}'.format(work_dir, target_file))
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name))
    except Exception as e:
        print(e)

    return {'tool': 'redfinger', 'result': result}

if __name__ == '__main__':
    target = ['https://www.ohlinge.cn',
              'http://124.115.216.186:8088',
              'http://111.74.153.159:7312',
              'https://sxqxt.sxydjthb.cn', ]
    print(run(target))
