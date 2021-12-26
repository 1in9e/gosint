#!/usr/bin/env python
# -*- coding: utf-8 -*-
from celery import Celery
import os
from time import time
import json
import requests

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

app = Celery('gosint.fileleak', broker=broker, backend=backend, )
app.config_from_object('config')

headers = {'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.15(0x17000f31) NetType/WIFI Language/zh_CN'}

@app.task
def run(target, wordlist='top100'):
    result = []
    work_dir = FILEPATH + '/tools'
    # 生成文件
    target_file = 'url_tmp_{}.txt'.format(time())
    file = open(work_dir + '/' + target_file, 'w');
    for tag in target:
        file.write(tag + '\n');
    file.close();

    out_file_name = '{}.txt'.format(time())     # fileleak.py
    if wordlist == 'top100':
        dictfile = work_dir + '/dicts/file_top_100.txt'
    elif wordlist == 'top2000':
        dictfile = work_dir + '/dicts/file_top_2000.txt'
    elif wordlist == 'top8000':
        dictfile = work_dir + '/dicts/file_top_8000.txt'
    else:
        # 留待补充
        dictfile = work_dir + 'dicts/file_top_100.txt'
    # 执行命令 ./fileleak.py --target http://www.ohlinge.cn --output 1234.txt
    if DEBUG == 'True':
        command = ['python3', 'fileleak.py', '--target', target_file, '--dict', dictfile, '--output', out_file_name]
        proxies = {'http': 'http://127.0.0.1:7777', 'https': 'http://127.0.0.1:7777'}
    else:
        command = ['python3', 'fileleak.py', '--target', target_file, '--dict', dictfile, '--output', out_file_name]
        proxies = {'http': 'http://127.0.0.1:7777', 'https': 'http://127.0.0.1:7777'}
    try:
        sb = SubProcessSrc(command, cwd=work_dir).run()
        if sb['status'] == 0:
            # 运行成功，读取json数据返回
            with open('{}/{}'.format(work_dir, out_file_name), 'r') as f:
                path = f.readlines()
                for line in path:
                    try:
                        dic = {}
                        url = line.split(']')[-1].split('\n')[0]
                        urlres = urlparse(url)
                        dic["host"] = urlres.scheme + "://" + urlres.netloc
                        dic["path"] = urlres.path
                        dic['cms'] = ''
                        dic["content-length"] = line.split('[')[-1].split(']')[0]
                        dic["status-code"] = line.split('[')[1].split(']')[0]
                        dic["title"] = line.split('[')[2].split(']')[0]
                        if int(dic["content-length"]) > 0:
                            result.append(dic)
                        # 将结果导入xray被动监听地址
                        try:
                            requests.get(url=url, headers=headers, proxies=proxies, timeout=3)
                        except Exception as e:
                            print(e)
                    except Exception as e:
                        print(e)
    except Exception as e:
        print(e)

    try:
        os.system('rm -rf {}/{}'.format(work_dir, out_file_name))
        os.system('rm -rf {}/{}'.format(work_dir, target_file))
    except:
        pass

    return {'tool': 'fileleak', 'result': result}

if __name__ == '__main__':
    target = ['https://www.ohlinge.cn',]
    print(run(target))
