#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libs.data import (
    scan_result,
    scan,
    target,
    system_settings
)
from gosint.celery import app
from celery.result import AsyncResult
from apps.assets.models import Port, IP
import IPy
import re
from time import sleep
from functools import reduce


def port_scan(is_port_api, wordlist='top100'):
    """
    naabu端口扫描
    :return:
    """
    scan_queue = []
    if system_settings.debug:
        print(len(scan_result.ip))

    print("[+] Running port_scan...")
    # 多IP列表同时发往客户端 lin9e 2021.7.31
    # naabu遇防护设备导致扫描结果全端口开放bug, 一次先传送一个！ lin9e 2021.10.19
    for i in range(0, len(scan_result.ip), 1):
        ips = scan_result.ip[i:i+1]
        naabu_scan = app.send_task('naabu.run', args=(ips, wordlist,), queue='naabu')
        scan_queue.append(AsyncResult(naabu_scan.id))
        # if is_port_api:
        #     port_api_scan = app.send_task('port_api.run', args=(ips,), queue='port_api')
        #     scan_queue.append(AsyncResult(port_api_scan.id))
    if is_port_api:
        for ipc in scan_result.ipc:
            if int(ipc['count']) > 8:
                port_api_scan = app.send_task('port_api.run', args=([ipc['ipc']],), queue='port_api')
                scan_queue.append(AsyncResult(port_api_scan.id))
    while True:
        for task in scan_queue:
            if task.successful():
                # 进行端口扫描并取出返回的结果
                if task.result['result']:
                    naabu_result = task.result['result']
                    port_list = []
                    for _ in naabu_result:
                        try:
                            ip = _['ip']
                            port = int(_['port'])
                            server = _['server']
                            # fofa查询出来IP对应的域名信息, 暂且记录于service中 by _lin9e in 2021.9.23
                            if task.result['tool'] == 'port_api':       # port_api暂仅用于c段查询
                                try:
                                    if not re.match(r'(?:[0-9]{1,3}\.){3}(?:[0-9]){1,3}(?:\/\d*)?(?:\-\d*)?', _['host'].split('//')[-1]):
                                        host = _['host']
                                        server = str(server) + '<br>' + str(host)
                                    ip_port = '{}:{}'.format(ip, port)
                                    port_list.append(Port(port=port, scan=scan.task, service=server,
                                                              ip_port=ip_port, tools='C段'))
                                    scan_result.webport.append({'domain': ip, 'port': port})
                                except Exception as e:
                                    print(e)
                            else:
                                # TODO get or filter?
                                father_ip_list = IP.objects.filter(ip=ip)
                                for father_ip in father_ip_list:
                                    ip_port = '{}:{}'.format(father_ip, port)
                                    port_list.append(Port(port=port, scan=scan.task, service=server, ip=father_ip, ip_port=ip_port, tools=task.result['tool']))
                                    # 80,443同时存在的情况下，只记录一次80, 配合webcontent_scan中httpx只推入domain部分
                                    # 见domaininfo.py
                                    if port == 80 or port == 443:
                                        pass
                                    else:
                                        if father_ip.subdomain:  # 如果有域名的情况下
                                            scan_result.webport.append({'domain': father_ip.subdomain, 'port': port})
                                        else:
                                            scan_result.webport.append({'domain': ip, 'port': port})
                        except Exception as e:
                            print(e)
                            continue
                    Port.objects.bulk_create(port_list, ignore_conflicts=True)
                scan_queue.remove(task)
            elif task.failed():
                scan_queue.remove(task)
        if not scan_queue:
            break
        sleep(0.5)    # fix bug: 2021.1.14: 修复单核cpu占用过高问题

    """
    # scan_result.webport 去重问题 Done by _Lin9e 2021.7.27
    naabu port_api结果端口去重TODO
    参考：
    from functools import reduce
    def delete_duplicate(data):
        func = lambda x, y: x + [y] if y not in x else x
        data = reduce(func, [[], ] + data)
        return data
    """
    #  暂时去掉去重 2021.8.20
    # def delete_duplicate(data):
    #     func = lambda x, y: x + [y] if y not in x else x
    #     data = reduce(func, [[], ] + data)
    #     return data
    # try:
    #     scan_result.webport = delete_duplicate(scan_result.webport)
    # except Exception as e:
    #     print(e)
    print("[+] Finish port_scan. Counts of port is {}".format(str(len(scan_result.webport))))