#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/30 2:32 下午
# @Author  : _lin9e
# @File    : certip_scan.py.py

from libs.data import (
    target,
    scan_result,
    scan,
    system_settings
)
from gosint.celery import app
from celery.result import AsyncResult
from apps.assets.models import IP, SubDomain
from time import sleep

def certip_scan():
    """
    利用Cert证书获取IP列表
    :return:
    """
    scan_queue = []
    print("[+] Running Cert IP scan...")
    for domain in target.need_subdomain:
        """
        certip module
        """
        cert2ip_scan = app.send_task('certip.run', args=([domain],), queue='certip')
        scan_queue.append(AsyncResult(cert2ip_scan.id))
    while True:
        for task in scan_queue:
            if task.successful():
                if task.result['result']:
                    if system_settings.debug:
                        print(task)
                        print(task.result['result'])
                    try:
                        temp = []
                        for _ in task.result['result']:
                            ip = _['ip']
                            if ip not in scan_result.ip:
                                temp.append(IP(ip=ip, scan=scan.task, is_cdn=False, tools='cert'))
                                scan_result.ip.append(ip)
                        IP.objects.bulk_create(temp, ignore_conflicts=True)
                    except Exception as e:
                        print(e)
                scan_queue.remove(task)
            if task.failed():
                scan_queue.remove(task)
        if not scan_queue:
            break
        sleep(0.5)

    # 扫描IP去重 2021.7.30 by _lin9e
    try:
        scan_result.ip = list(set(scan_result.ip))
    except Exception as e:
        print(e)

    print("[+] Finish certip_scan. Counts of ip is {}!".format(str(len(scan_result.ip))))


