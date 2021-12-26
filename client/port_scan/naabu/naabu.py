#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery import Celery
import os
from time import time
import json

from libs.process import SubProcessSrc
from xml.dom.minidom import parse

FILEPATH = os.path.split(os.path.realpath(__file__))[0]

if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'False':
    broker = os.environ['BROKER']
    backend = os.environ['BACKEND']
    DEBUG = "False"
else:
    DEBUG = "True"
    broker = 'redis://127.0.0.1:6379/0'
    backend = 'redis://127.0.0.1:6379/2'

app = Celery('gosint.naabu', broker=broker, backend=backend, )
app.config_from_object('config')


@app.task
def run(target, wordlist='top100'):
    work_dir = FILEPATH + '/tools'

    # 生成文件
    target_file = 'ips_tmp_{}.txt'.format(time())
    file = open(work_dir + '/' + target_file, 'w');
    for tag in target:
        file.write(tag + '\n');
    file.close();

    if wordlist == 'all':
        portfile = work_dir + '/portfile_all.txt'
    elif wordlist == 'top1000':
        portfile = work_dir + '/portfile_top1000.txt'
    elif wordlist == 'top100':
        portfile = work_dir + '/portfile_top100.txt'
    else:
        portfile = work_dir + '/portfile_top10.txt'
    # portfile_test = work_dir + '/portfile_top10.txt'

    nmap_file = 'naabu_result_{}.xml'.format(time())
    naabu_nmap_cmd = 'nmap -sV -oX {}'.format(nmap_file)
    out_file_name = '{}_{}.json'.format('out_file', time())

    # 执行命令 ./naabu -iL target_file -ports-file portfile.txt -json -o port.txt -nmap -top-ports 100
    if DEBUG == 'True':
        command = ['./naabu_mac', '-silent', '-iL', target_file, '-ports-file', portfile, '-json', '-o', out_file_name, '-nmap-cli',
                   naabu_nmap_cmd]
    else:
        command = ['./naabu', '-silent', '-iL', target_file, '-ports-file', portfile, '-json', '-o', out_file_name, '-nmap-cli',
                   naabu_nmap_cmd]

    result = []
    # 整体抛出异常以防naabu本身出错
    try:
        sb = SubProcessSrc(command, cwd=work_dir).run()
        if sb['status'] == 0:
            # 运行成功，读取json数据返回
            with open('{}/{}'.format(work_dir, out_file_name), 'r') as f:
                port = f.readlines()
                if len(port) < 100:     # 剔除一扫全开放的bug
                    for line in port:
                        # print(line)
                        dic = {}
                        # 如果没有任何端口开放抛出异常
                        try:
                            dic["host"] = ''
                            # 如果传入ip，则没有host字段，抛出异常
                            try:
                                dic["host"] = str(json.loads(line)['host'])
                            except:
                                pass
                            dic["ip"] = str(json.loads(line)['ip'])
                            dic["port"] = json.loads(line)['port']
                            dic["server"] = ""
                            print(dic)
                            result.append(dic)
                        except:
                            pass

            # 打开xml，读取nmap的结果,没有port开放的话，抛出异常
            try:
                tree = parse('tools/' + nmap_file);
                root = tree.documentElement
                port_length = len(root.getElementsByTagName('ports')[0].childNodes)
                for i in range(0, port_length, 2):
                    server = root.getElementsByTagName('ports')[0].childNodes[i].childNodes[1].getAttribute("name")
                    port = int(root.getElementsByTagName('ports')[0].childNodes[i].getAttribute("portid"))
                    # 加入字典中
                    for res in result:
                        if (port == res['port']):
                            res["server"] = str(server)
            except Exception as e:
                print(e)
            # 当naabu出错，导致生成不了文件时，抛出异常
            try:
                os.system('rm -rf {}/{}'.format(work_dir, target_file))
                os.system('rm -rf {}/{}'.format(work_dir, out_file_name))
                os.system('rm -rf {}/{}'.format(work_dir, nmap_file))
            except:
                pass
    except Exception as e:
        print(e)
    return {'tool': 'naabu', 'result': result}


if __name__ == '__main__':
    list1 = [
        '125.66.152.242', ]
    print(run(list1, wordlist='top10'))
