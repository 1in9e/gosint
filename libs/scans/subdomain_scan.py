#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libs.data import (
    target,
    scan_result,
    scan,
    system_settings
)
from gosint.celery import app
from celery.result import AsyncResult
from apps.assets.models import SubDomain, BlockAssets
from time import sleep


def all_subdomain_scan():
    blocks = [_.assets for _ in BlockAssets.objects.all()]
    """
    子域名扫描
    :return:
    """
    scan_queue = []
    print("[*] Running subdomain scanning...")
    for domain in target.need_subdomain:
        """
        subfinder子域名扫描
        """
        subfinder_scan = app.send_task('subfinder.run', args=(domain,), queue='subfinder')
        scan_queue.append(AsyncResult(subfinder_scan.id))
        if system_settings.debug:
            """
            debug模式只使用subfinder进行扫描
            """
            continue
        """
        ksubdomain无状态子域名爆破
        """
        ksubdomain_scan = app.send_task('ksubdomain.run', args=(domain,), queue='ksubdomain')
        scan_queue.append(AsyncResult(ksubdomain_scan.id))
        """
        xray子域名收集
        """
        xraydomain_scan = app.send_task('xray_subdomain.run', args=(domain,), queue='xray_subdomain')
        scan_queue.append(AsyncResult(xraydomain_scan.id))

    while True:
        for task in scan_queue:
            if task.successful():
                temp = []
                # domain_result = task.result
                if system_settings.debug:
                    print(task)
                    print(task.result['result'])
                if task.result['result']:
                    for domain in task.result['result']:
                        try:
                            # domain strip add 2021.8.14
                            domain = domain.strip()
                            # DONE：根据黑名单去除泛解析的域名
                            if any(ban in domain for ban in blocks):
                                continue
                            sub = SubDomain(subdomain=domain, scan_task=scan.task, tools=task.result['tool'])
                            temp.append(sub)
                            scan_result.domain.append(domain)
                        except Exception as e:
                            print(e)
                    sleep(0.5)  # 修复可能插入重复subdomain的问题
                    SubDomain.objects.bulk_create(temp, ignore_conflicts=True)
                scan_queue.remove(task)
            if task.failed():
                scan_queue.remove(task)
        if not scan_queue:
            break
        sleep(0.5)
    # if system_settings.debug:
    #     # debug 模式下只存放前10个域名
    #     scan_result.domain = scan_result.domain[:10]

    # 子域名去重 2021.7.27 by _lin9e
    try:
        scan_result.domain = list(set(scan_result.domain))
    except Exception as e:
        print(e)

    print("[+] Finish subdomain_scan. Counts of subdomain is {}!".format(str(len(scan_result.domain))))



