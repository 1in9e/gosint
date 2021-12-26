#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libs.data import (
    scan_result,
    scan,
    system_settings,
    target
)
from gosint.celery import app
from celery.result import AsyncResult
from apps.assets.models import SubDomain, IP, Port, IPC
from time import sleep
import IPy, re


def domaininfo_scan():
    """
    域名信息收集
    :return:
    """
    # DONE: 先处理target.domain中的domain信息
    if target.domain:
        temp_domain = []
        if system_settings.debug:
            print(len(target.domain))
        for _ in target.domain:
            _ = _.strip()
            try:
                if _ not in scan_result.domain:
                    temp_domain.append(SubDomain(subdomain=_, scan_task=scan.task, tools='手工导入'))
                    scan_result.domain.append(_)
            except Exception as e:
                print(e)
                print(_)
                continue
        SubDomain.objects.bulk_create(temp_domain, ignore_conflicts=True)

    scan_queue = []
    if system_settings.debug:
        print(len(scan_result.domain))
    print("[+] Running domaininfo_scan...")
    # 多domain同时发送客户端, 以10个列表的额度发送到客户端，客户端结果接收服务端增加多result处理 by _lin9e 2021.7.28
    for i in range(0, len(scan_result.domain), 50):
        domains = scan_result.domain[i:i+50]
        domaininfo_scan = app.send_task('domaininfo.run', args=(domains,), queue='domaininfo')
        scan_queue.append(AsyncResult(domaininfo_scan.id))
    while True:
        for task in scan_queue:
            if task.successful():
                if task.result['result']:
                    for domaininfo_result in task.result['result']:
                        try:
                            domain = domaininfo_result['domain']
                            domain_type = domaininfo_result['type']
                            domain_record = ','.join(domaininfo_result['record'])
                            domain_ips = domaininfo_result['ips']
                            sub = SubDomain.objects.get(subdomain=domain)
                            sub.domain_type = domain_type
                            sub.record = domain_record
                            sub.domain_ips = domain_ips
                            sub.save()
                            domain_ips_list = []
                            # 是不是CND，都添加到webport==80中，用于web发现、其他端口，则正常通过端口扫描到web发现的过程
                            scan_result.webport.append({'domain': domain, 'port': 80})
                            if len(domain_ips) < 2:  # 如果一个域名解析的ip地址大于1个，则判定为CDN地址
                                cdn = False
                            else:
                                cdn = True
                                # TODO: cdn结果的端口插入问题
                                # Port.objects.get_or_create(port='80', scan=scan.task, service='', ip=ip,
                                #                            ip_port=ip_port, tools=task.result['tool'])
                            for ip in domain_ips:
                                domain_ips_list.append(IP(ip=ip, scan=scan.task, subdomain=sub, is_cdn=cdn, tools='subdomain'))
                                # fix bug: 2021.1.14: 如果为CDN的话，则不去扫描端口，而直接将域名添加到webport，进行httpx扫描
                                # 内网IP则直接不扫端口，IPy.IP(ip).iptype() == 'PUBLIC' add by _lin9e 2021.8.5
                                # 内网ip扫描 - 2021.12.13
                                # if not cdn and IPy.IP(ip).iptype() == 'PUBLIC':
                                if not cdn:
                                    scan_result.ip.append(ip)
                            IP.objects.bulk_create(domain_ips_list)
                        except Exception as e:
                            print(domaininfo_result['domain'])
                            print(e)
                            continue
                scan_queue.remove(task)
            elif task.failed():
                scan_queue.remove(task)
        if not scan_queue:
            break
        sleep(0.5)    # fix bug: 2021.1.14: 修复单核cpu占用过高的问题

    # DONE: 处理target.ip中的ip信息，如果有网段，需要解析网段
    # TODO：需要先判断ip是否存活
    # DONE：判断内网ip，如果是内网ip，直接跳过端口扫描(解析到的IP)，直接添加的内网IP则可以扫描
    if target.ip:
        temp_ip = []
        print(target.ip)
        for _ in target.ip:
            try:
                results = IPy.IP(_)
                for ip in results:
                    temp_ip.append(IP(ip=str(ip), scan=scan.task))
                    scan_result.ip.append(str(ip))
                    scan_result.webport.append({'domain': ip, 'port': 80})
            except Exception as e:
                print(e)
                print(ip)
                continue
        IP.objects.bulk_create(temp_ip, ignore_conflicts=True)

    # 扫描IP去重 2021.7.27 by _lin9e
    try:
        scan_result.ip = list(set(scan_result.ip))
    except Exception as e:
        print(e)

    print("[+] Finish domaininfo_scan. Counts of no_cdn and no_priv ip is {}! Counts of all 80 web is {}".format(
        str(len(scan_result.ip)), str(len(scan_result.webport))))
    # if system_settings.debug:
    #     # debug模式下只存5个ip进行扫描
    #     scan_result.ip = scan_result.ip[:5]
    #     print(scan_result.ip)

    """
    IPC C段情报统计 add by _lin9e in 2021.9.9
    """
    print("[*] Running IP C line...")
    try:
        ipcs = []   # django添加数组
        ipc_list = []    # 整理C段
        for ip in scan_result.ip:
            ipc_list.append(re.findall(r'\d+?\.\d+?\.\d+?\.', ip)[0] + '0/24')
        count_ipc = dict()  # C段IP及对应主机数量字典
        for item in ipc_list:
            if item in count_ipc:
                count_ipc[item] += 1
            else:
                count_ipc[item] = 1
        for ip_c in count_ipc:
            try:
                ipcs.append(IPC(ipc=ip_c, ipc_count=count_ipc[ip_c], scan=scan.task))
                scan_result.ipc.append({'ipc': ip_c, 'count': count_ipc[ip_c]})
            except Exception as e:
                print(e)
        IPC.objects.bulk_create(ipcs)
        print("[+] Finish IP C line, count of C is {}".format(len(count_ipc)))
    except Exception as e:
        print(e)



