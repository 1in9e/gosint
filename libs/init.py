#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libs.data import (
    target,
    scan,
    scan_result,
    system_settings,
    engine,
)
from apps.targetApp.models import Target
from apps.scans.models import Scans
from apps.scanEngine.models import EngineType
from django.conf import settings
from time import sleep
import ipaddress


def system_init():
    """
    系统参数初始化
    1. 是否是debug模式
    :return:
    """
    if settings.DEBUG:
        system_settings.debug = True
    else:
        system_settings.debug = False


def target_init(target_id_list):
    """
    初始化，获取扫描目标，扫描引擎，以及初始化各个存储模块
    :return:
    """
    target.domain = []  # 直接提供子域名的目标
    target.need_subdomain = []   # 需要子域名扫描的目标
    target.ip = []  # 直接提供ip的目标
    # target.web = []
    # 将target分别查询出来进行分类存储
    for _ in target_id_list:
        t = Target.objects.get(pk=_)
        if t.target_type == 'domain':
            domain_temp = t.target_name
            if domain_temp.startswith('.'):
                # 需要进行子域名扫描，放入子域名扫描存储
                target.need_subdomain.append(t.target_name.strip('.').strip())
            else:
                target.domain.append(t.target_name.strip())
        if t.target_type == 'ip':
            ip_format = t.target_name.strip()
            # IP段格式化处理 by _lin9e in 2021.9.9
            if '-' in ip_format:
                tmp = ip_format.split('.')
                for _ in range(int(tmp[-1].split('-')[0]), int(tmp[-1].split('-')[1])):
                    ip = "{}.{}.{}.{}".format(tmp[0], tmp[1], tmp[2], _)
                    target.ip.append(ip.strip())
            elif '/' in ip_format:
                sub_nets = ipaddress.IPv4Network(ip_format, strict=False).hosts()
                for sub_net in sub_nets:
                    target.ip.append(str(sub_net))
            else:
                target.ip.append(ip_format)

def engine_init(scan_type_id):
    """
    扫描引擎初始化
    :return:
    """
    t = EngineType.objects.get(pk=scan_type_id)
    # 是否扫描子域名
    engine.subdomain_discovery = t.subdomain_discovery
    # 是否证书获取IP
    engine.certip_scan = t.certip_scan
    # 是否扫描端口
    engine.port_scan = t.port_scan
    # 是否开启port_api
    engine.port_api = t.port_api
    # 端口扫描类型： top10 top100 top1000 all
    engine.port_scan_type = t.port_scan_type
    # 是否发现web
    engine.fetch_url = t.fetch_url
    # 是否扫描路径，包含fileleak jsfinder
    engine.dir_file_search = t.dir_file_search
    # 扫描目录类型，指fileleak字典： top100 top2000 top8000
    engine.dir_file_type = t.dir_file_type
    # 是否扫描漏洞，指nuclei
    engine.vuln_nuclei = t.vuln_nuclei
    # 是否扫描漏洞，指rad2xray
    engine.vuln_xray = t.vuln_xray



def scantask_init(scan_task_id):
    """
    扫描任务初始化
    :param scan_task_id:
    :return:
    """
    sleep(3)    # 暂停3秒，等数据库插入。fix bug：小概率任务插入失败的情况，提示scan任务未找到
    scan_task = Scans.objects.get(pk=scan_task_id)
    scan.task = scan_task


def result_init():
    """
    子域名扫描结果栈初始化
    :return:
    """
    scan_result.domain = []
    scan_result.ip = []
    scan_result.ipc = []
    scan_result.webport = []
    scan_result.webapp = []




