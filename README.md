# gosint
[![Build Status](https://travis-ci.org/1in9e/gosint.svg?branch=master)](https://travis-ci.org/1in9e/gosint)
[![simpleui](https://img.shields.io/badge/developing%20with-Simpleui-2077ff.svg)](https://github.com/newpanjing/simpleui)
[![python](https://img.shields.io/badge/python-3.6|3.7|3.8-blue)](https://github.com/1in9e/gosint/tree/main/)

## 简介
在开始使用之前，请务必阅读并同意[免责声明](./thirdparty/免责声明.md)中的条款，否则请勿下载安装使用本系统。
> gosint, srchunter全新出发， 一款分布式资产信息收集与管理和漏洞扫描工具
>
```
    1. 实现原理简单，可根据个人挖洞经验进行扩展
    2. 支持分布式部署，取决于你的财力(主机数量多少);客户端可部署于vps/pc/laptop...
    3. docker一键化部署
    4. 漏洞实时通知
    5. 扫描引擎可自定义
```
## 原理
![info](thirdparty/gosint_info.jpg)

## Usage
### 使用前须知
扫描插件中使用了一些优秀的工具，其中部分工具所需license、接口api token等需自行添加
#### xray高级版license
将xray-license.lic分别添加到如下位置即可:(xray配置文件需自行配置/如reverse等)
```
gosint/client/subdomain_scan/xray_subdomain/tools/
gosint/client/vuln_scan/rad2xray/tools/
```
#### Client Config
- C段存活/端口依赖于fofa，需配置fofa api
- 域名CNAME黑名单
```
gosint/client/config.yaml
```
#### 通知
> 支持邮件/企业微信机器人提醒通知功能，其他可通过libs/common.py扩展
> 
更改django配置文件中邮件及企业微信机器人token即可实现机器人通知功能

#### 其他Tools配置项请自行配置
...

### 生产环境版
```
默认情况下，gosint中间件所使用账号密码分别为gosintuser、gosintpass，Web应用账号密码分别为gosint、GosintPassword
请在生产环境下替换为强密码
# 中间件账号密码需替换文件:(建议全局关键字搜索替换)
gosint/docker-compose.yml
gosint/client/docker-compose.yml
gosint/gosint/setting-prod.py
gosint/supervisor/supervisord.conf

# Web应用账号密码需替换文件：
gosint/docker-entrypoint.sh
```

#### 单一服务器部署
生产环境搭建，采取docker化部署的方案
> 服务器需安装docker / docker-compose, 请自行安装
```
cd gosint/
docker-compose up -d --build
```

_! 为了避免xray webhook被人恶意塞数据，建议对webhook url path进行修改，直接改如下两处即可：_
```
gosint/apps/dashboard/urls.py
gosint/client/docker-entrypoint.sh
```

#### 分布式部署
分布式部署依赖于celery的任务调度，通过Celery Broker将任务分发到不同的客户端，调度work再通过Celery Backend异步获取执行后的结果，本应用分别采用了RabbitMQ、Redis作为broker、backend，所以需要确保服务端相应端口开放
##### 服务端
```
cd gosint/
docker-compose up -d --build
```

##### 客户端(可部署多个)
客户端位于gosint/client目录, 单独讲client上传至客户端VPS即可，无需拷贝服务端代码
> 某一个节点开启哪些扫描功能通过client/config.ini配置, 扫描插件列表如下:
```
# true or false对应相应的扫描插件是否启用
subfinder=true
ksubdomain=true
xray_subdomain=true
certip=false
# domaininfo=true
httpx=true
naabu=true
port_api=true
fileleak=true
jsfinder=true
nuclei=true
rad2xray=true
redfinger=true
```
客户端节点开启方式:
```
cd client/
# 插件选用控制
vim config.ini
# 更改服务端IP
vim docker-compose.yml 
# 开启节点
docker-compose up -d --build
```
需注意，客户端docker-compose.yml中需要修改服务端地址：
- BROKER
- BACKEND
- SERVER_URL (用于xray webhook接收)

### 本地开发调试版
> 需要分别部署Web服务端、Celery Servicer端及Client端及redis. 注意调试模式"debug"下客户端执行Mac可执行文件，Windows需自行下载客户端可执行文件，并修改相应位置代码
#### Web服务端
```
pip3 install -r requirements.txt
# Django
python3 manage.py migrate
python3 manage.py runserver
```

#### Server端
```
# 当前位置下执行
python3 -m celery -A gosint  worker -Q server -n server -l info
```

#### Client端
需要到./client/下各个客户端目录中执行相应Celery，将其中的docker-entrypoint.sh用python3执行即可
```
# 例如fileleak
python3 -m celery -A fileleak worker -l info -Q fileleak
```

#### Redis
> 建议docker一键启动
```
docker run -it -d -p 6379:6379 redis redis-server
```
#### Pycharm开发环境
```
# mac 设置python3虚拟环境
cd ~
virtualenv  -p /usr/bin/python3  py3env
# 终端进入py3env虚拟环境
source ~/py3env/bin/activate
```

### 节点任务监控
gosint可采用Celery flower对节点任务进行监控
#### 生产环境开启监控
开启服务端docker前修改如下文件配置自启动即可
gosint/supervisor/supervisord.conf
```
[program:flower]
...
autostart=true
```
对应生产环境的节点任务监控，也可以在本地计算机运行如下命令即可在本地进行监控
```
# flower 本地监控
celery flower --broker=amqp://gosintuser:gosintpass@8.8.8.8:25672/gosint
```
#### 本地开发调试环境启动任务监控
```
celery flower -A gosint
```

## 预览
![](thirdparty/1.png)
![](thirdparty/2.png)
![](thirdparty/3.png)
![](thirdparty/4.png)
![](thirdparty/5.png)

## Version
### V1.0.0
- open source
- from gosint_priv to gosint

## TODO
- 主机扫描
- 优化过程

## Thanks
1. gosint参考了许多优秀的开源项目，它们包括但不限于：
   - https://github.com/le31ei/srchunters
   - https://github.com/yogeshojha/rengine
   - https://github.com/TophantTechnology/ARL
   - https://github.com/projectdiscovery/naabu
   - https://github.com/projectdiscovery/subfinder
   - https://github.com/projectdiscovery/nuclei
   - https://github.com/projectdiscovery/httpx
   - https://github.com/Threezh1/JSFinder
   - https://github.com/chaitin/xray
2. gosint banner及logo图设计来自于我的女朋友