#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery import shared_task
from libs.init import (
    system_init,
    target_init,
    engine_init,
    scantask_init,
    result_init,
)
from libs.data import (
    target,
    scan_result,
    engine,
)
from libs.scans.subdomain_scan import all_subdomain_scan
from libs.scans.certip_scan import certip_scan
from libs.scans.domaininfo import domaininfo_scan
from libs.scans.port_scan import port_scan
from libs.scans.webcontent_scan import httpx_scan, vuln_scan


@shared_task
def task_worker(target_id_list, scan_type_id, scan_task_id):
    """
    任务调度的worker，负责对子模块进行调度，判断是否扫描成功，是否返回结果
    :param target: 扫描目标
    :param scan_type: 扫描引擎（fullscan or 自定义）
    :param scan_task_id: 扫描任务的id
    :return:
    """
    # 系统初始化
    system_init()
    # 目标初始化
    target_init(target_id_list)
    # 扫描引擎初始化
    engine_init(scan_type_id)
    # 扫描任务初始化
    scantask_init(scan_task_id)
    # 结果栈初始化
    result_init()

    if target.need_subdomain and engine.subdomain_discovery:
        """
        子域名扫描
        """
        all_subdomain_scan()

    # target.domain or scan_result.domain
    if target.domain or scan_result.domain or target.ip:
        """
        域名信息扫描
        """
        domaininfo_scan()

    if engine.certip_scan:
        """
        cert ip 信息收集
        """
        certip_scan()

    if target.ip or scan_result.ip:
        """
        端口扫描
        """
        if engine.port_scan:
            # engine.port_scan_type 为端口扫描类型传参
            port_scan(engine.port_api, engine.port_scan_type)
    if scan_result.webport and engine.fetch_url:
        """
        http header扫描
        """
        httpx_scan()

    # 漏洞三合一：三步不再前后排列，而是同时进行扫描 by _lin9e in 21.7.18
    if scan_result.webapp:
        # vuln_scan:
        # engine.dir_file_search        if_fileleak
        # engine.vuln_nuclei            if_nuclei
        # engine.vuln_xray              if_xray
        # engine.dir_file_type          wordlist
        if engine.dir_file_search or engine.vuln_nuclei or engine.vuln_xray:
            vuln_scan(engine.dir_file_search, engine.vuln_nuclei, engine.vuln_xray, engine.dir_file_type)
        """
        vuln_scan包含nuclei_scan\ fileleak_scan \ rad2xray_scan
        """




