#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/12/21 15:30
# @Author  : _lin9e
from celery import Celery
import os, yaml
from time import time
import json
import dns.resolver

FILEPATH = os.path.split(os.path.realpath(__file__))[0]

if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'False':
    broker = os.environ['BROKER']
    backend = os.environ['BACKEND']
    DEBUG = "False"
else:
    DEBUG = "True"
    broker = 'redis://127.0.0.1:6379/0'
    backend = 'redis://127.0.0.1:6379/2'

app = Celery('gosint.domaininfo', broker=broker, backend=backend, )
app.config_from_object('config')

# get fofa email key
def get_cname_blacklist():
    with open(os.path.join(FILEPATH, '../../config.yaml')) as f:
        y = yaml.load(f, Loader=yaml.SafeLoader)
    cname_blacklist = y['CNAME_BLACKLIST']
    return cname_blacklist

### func:get_ip and func:get_cname
def get_ip(domain, log_flag = True):
    domain = domain.strip()
    ips = []
    try:
        answers = dns.resolver.query(domain, 'A')
        for rdata in answers:
            ips.append(rdata.address)
    except dns.resolver.NXDOMAIN as e:
        if log_flag:
            print("{} {}".format(domain, e))

    except Exception as e:
        if log_flag:
            print("{} {}".format(domain, e))

    return ips
def get_cname(domain, log_flag = True):
    cnames = []
    try:
        answers = dns.resolver.query(domain, 'CNAME')
        for rdata in answers:
            cnames.append(str(rdata.target).strip(".").lower())
    except dns.resolver.NoAnswer as e:
        if log_flag:
            print(e)
    except Exception as e:
        if log_flag:
            print("{} {}".format(domain, e))
    return cnames

@app.task
def run(domains):
    result = []
    cname_blacklist = get_cname_blacklist()
    for domain in domains:
        try:
            ips = get_ip(domain)
            if ips:
                cnames = get_cname(domain, False)
                info = {
                    "domain": domain,
                    "type": "A",
                    "record": ips,
                    "ips": ips
                }
                if cnames:
                    # 加入cname黑名单过滤 add by 1in9e in 2021.11.2
                    if any(ban in cnames for ban in cname_blacklist):
                        continue
                    else:
                        info["type"] = 'CNAME'
                        info["record"] = cnames
                result.append(info)
        except Exception as e:
            print(e)
    return {'tool': 'domaininfo', 'result': result}


if __name__ == '__main__':
    testlist = [
        "www.ohlinge.cn",
        "shop34536645.taobao.com"
    ]
    list2 = ['www.ohlinge.cn']
    print(run(testlist))
