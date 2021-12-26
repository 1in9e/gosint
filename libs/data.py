#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libs.datatype import AttribDict


# 目标存储初始化
# target.need_subdomain: 存放需要进行子域名扫描的主域名， 类型：list
# target.domain：存放普通扫描端口和ip的域名，类型：list
# target.ip: 存放需要扫描的ip， 类型：list
target = AttribDict()

# 系统参数初始化
# system_settings.debug: 是否在debug模式
system_settings = AttribDict()

# 扫描相关参数存储初始化
# scan.task：存放当前的扫描任务对象
scan = AttribDict()

# 引擎相关参数初始化
engine = AttribDict()

# 扫描结果初始化
# 域名信息存放在：scan_result.domain
# ip收集信息存放在：scan_result.ip
# ip c段收集信息存放在： scan_result.ipc
# web端口信息存放在：scan_result.webport
# webapp信息存放：scan_result.webapp
scan_result = AttribDict()

# 黑名单初始化
# fix bug: python manage.py的时候会去自动发现执行admin.py中的代码
# 会导致from gosint.tasks import task_worker的执行，最后会
# 导致还没有migrate的时候，这里就执行了代码
# blocks = [_.assets for _ in BlockAssets.objects.all()]



