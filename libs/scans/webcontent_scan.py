#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libs.data import (
    scan_result,
    scan,
    system_settings
)
from gosint.celery import app
from celery.result import AsyncResult
from apps.assets.models import WebApp, FileLeak, Nuclei, Rad2xray, CrawlerURL, SubDomain, BlockAssets
from time import sleep
from libs.common import send_to_company, send_to_mail
from functools import reduce

def httpx_scan():
    """
    httpx扫描header等信息
    :return:
    """
    scan_queue = []
    if system_settings.debug:
        print(scan_result.webport)
    print("[+] Running httpx_scan for webfinder...")
    webport_list = []
    for web in scan_result.webport:
        # 2021.7.28 修改逻辑、将所有webport列表以每次取30个值的方式发送至客户端，客户端传入多个返回结果 by _lin9e
        if int(web['port']) in (80, 443):
            webport_list.append("{}".format(web['domain']))
        else:
            webport_list.append("{}:{}".format(web['domain'], web['port']))
    try:
        webport_list = list(set(webport_list))      # 去重
    except Exception as e:
        print(e)
    if system_settings.debug:
        print(webport_list)
    print("[*][httpx_scan] counts of webport is {}!".format(str(len(webport_list))))
    for i in range(0, len(webport_list), 50):
        webport_split = webport_list[i:i+50]
        httpx_scan = app.send_task('httpx.run', args=(webport_split,), queue='httpx')
        scan_queue.append(AsyncResult(httpx_scan.id))
    while True:
        for task in scan_queue:
            if task.successful():
                if task.result['result']:
                    webapp_list = []
                    for httpx_result in task.result['result']:
                        try:
                            # httpx_result = task.result['result'][0]
                            url = httpx_result['url']
                            content_length = httpx_result['content-length']
                            status_code = httpx_result['status-code']
                            title = httpx_result['title']
                            webserver = httpx_result['webserver']
                            # webapp, created = WebApp.objects.get_or_create(url=url, content_length=content_length,
                            #                                                status_code=status_code, title=title,
                            #                                                webserver=webserver, scan=scan.task)
                            webapp_list.append(WebApp(url=url, content_length=content_length, status_code=status_code, title=title, webserver=webserver, scan=scan.task))
                            # scan_result.webapp.append({'url': url, 'webapp': webapp})
                            scan_result.webapp.append(url)
                        except Exception as e:
                            print(e)
                            continue
                    WebApp.objects.bulk_create(webapp_list, ignore_conflicts=True)
                scan_queue.remove(task)
            elif task.failed():
                scan_queue.remove(task)
        if not scan_queue:
            break
        sleep(0.5)         # fix bug: 2021.1.14: 修复单核cpu占用过高问题

    # # scan_result.webapp 去重 by _lin9e 2021.7.27
    # def delete_duplicate(data):
    #     func = lambda x, y: x + [y] if y not in x else x
    #     data = reduce(func, [[], ] + data)
    #     return data
    # # print(len(scan_result.webapp))
    # try:
    #     scan_result.webapp = delete_duplicate(scan_result.webapp)
    # except Exception as e:
    #     print(e)
    # try:
    #     scan_result.webapp = set(list(scan_result.webapp))
    # except Exception as e:
    #     print(e)
    print("[+] Finish web_finder(httpx_scan). Counts of webapp is {}!".format(str(len(scan_result.webapp))))

# DONE: 合并fileleak_scan & nuclei_scan, 并加入rad2xray_scan, 共同用作函数vuln_scan!
"""
def vuln_scan():
    fileleak_scan()
    nuclei_scan()
    rad2xray_scan()
"""
def vuln_scan(if_fileleak, if_nuclei, if_xray, wordlist='top100'):
    """
    漏洞扫描模块：fileleak 、 nuclei 、 rad2xray_scan
    :return:
    """
    scan_queue = []
    if system_settings.debug:
        print(scan_result.webapp)
    if if_nuclei and if_xray and if_fileleak:
        print("[+] Running vuln_scan all module ...")
    elif if_nuclei:
        print("[+] Running vuln_scan: nuclei...")
    elif if_xray:
        print("[+] Running vuln_scan: xray...")
    elif if_fileleak:
        print("[+] Running vuln_scan: fileleak...")
    else:
        print("[-] vuln_scan off!")
    for i in range(0, len(scan_result.webapp), 20):
        url_split_list = scan_result.webapp[i:i+20]
        """
        fileleak_scan module
        """
        if if_fileleak:
            # fileleak_scan = app.send_task('fileleak.run', args=("{}".format(web['url']), wordlist,), queue='fileleak')
            # scan_queue.append({"webapp": web['webapp'], 'task': AsyncResult(fileleak_scan.id)})
            fileleak_scan = app.send_task('fileleak.run', args=(url_split_list, wordlist,), queue='fileleak')
            scan_queue.append(AsyncResult(fileleak_scan.id))
            """
            jsfinder_scan module
            """
            jsfinder_scan = app.send_task('jsfinder.run', args=(url_split_list,), queue='jsfinder')
            scan_queue.append(AsyncResult(jsfinder_scan.id))
        """
        nuclei_scan module
        """
        if if_nuclei:
            nuclei_scan = app.send_task('nuclei.run', args=(url_split_list,), queue='nuclei')
            scan_queue.append(AsyncResult(nuclei_scan.id))
        """
        rad2xray_scan module
        """
        if if_xray:
            rad2xray_scan = app.send_task('rad2xray.run', args=(url_split_list,), queue='rad2xray')
            scan_queue.append(AsyncResult(rad2xray_scan.id))
        """
        rad2xray_scan module
        """
        redfinger_scan = app.send_task('redfinger.run', args=(url_split_list,), queue='redfinger')
        scan_queue.append(AsyncResult(redfinger_scan.id))

    blocks = [_.assets for _ in BlockAssets.objects.all()]
    while True:
        for task in scan_queue:
            if task.successful():
                if task.result['result']:
                    if task.result['tool'] == 'fileleak' or task.result['tool'] == 'jsfinder' or task.result['tool'] == 'redfinger':
                        # fileleak回收 fileleak & jsfinder & redfinger
                        for url_leak in task.result['result']:
                            try:
                                host = url_leak['host']
                                path = url_leak['path']
                                content_length = url_leak['content-length']
                                status_code = url_leak['status-code']
                                title = url_leak['title']
                                tools = task.result['tool']
                                cms = url_leak['cms']
                                FileLeak.objects.get_or_create(url=host+path, path=path, cms=cms,
                                                               scan=scan.task, content_length=content_length,
                                                               status_code=status_code,
                                                               title=title, tools=tools)
                                content = "### RedFinger \nurl:{url} \n重点指纹:{cms} \n请及时查看和处理".format(
                                    url=host, cms=cms)
                            except Exception as e:
                                print(e)
                                continue
                            # if task.result['tool'] == 'redfinger':
                            #     send_to_company('gosint 发现了新红队重点指纹', content)
                        # jsfinder 域名回收
                        if task.result['tool'] == 'jsfinder':
                            temp = []
                            try:
                                for domain in task.result['result_subdomain']:
                                    if any(ban in domain for ban in blocks):
                                        continue
                                    sub = SubDomain(subdomain=domain, scan_task=scan.task, tools=task.result['tool'])
                                    temp.append(sub)
                                SubDomain.objects.bulk_create(temp, ignore_conflicts=True)
                            except Exception as e:
                                print("[-] jsfinder to subdomains error.")
                                print(e)
                    elif task.result['tool'] == 'nuclei':
                        # nuclei回收
                        for line in task.result['result']:
                            try:
                                host = line['host']
                                templateID = line['templateID']
                                severity = line['severity']
                                matched = line['matched']
                                detail = line['detail']
                                Nuclei.objects.get_or_create(url=host, scan=scan.task,
                                                             templateID=templateID, severity=severity,
                                                             matched=matched, detail=detail, mark=False)
                                content = "### 漏洞名:{templateID}\n url:{url} \n详情:{detail} \n请及时查看和处理".format(
                                    url=matched, templateID=templateID, detail=detail
                                )
                            except Exception as e:
                                print(e)
                                continue
                            if severity != 'info':
                                send_to_company('gosint 发现了新漏洞', content)
                            elif severity in ('high', 'medium'):
                                send_to_mail('gosint 发现了新漏洞', content)
                    elif task.result['tool'] == 'rad2xray':
                        # rad2xray 回收:
                        # 2021.8.19 此处只回收rad爬虫url结果, xray扫描漏洞结果通过webhook方式 api接口回收
                        for line in task.result['result']:
                            try:
                                url = line['URL']
                                method = line['Method']
                                header = line['Header']
                                b64_body = line['b64_body'] if method == "POST" else ''
                                CrawlerURL.objects.get_or_create(scan=scan.task, url=url, method=method,
                                                                 header=header, b64_body=b64_body)
                            except Exception as e:
                                print(e)
                    else:
                        # and more
                        pass
                scan_queue.remove(task)
            elif task.failed():
                scan_queue.remove(task)
        if not scan_queue:
            break
        sleep(0.5)
