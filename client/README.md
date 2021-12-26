# gosint_client部署说明 
> 新增一键部署，客户端只需要./client/目录下面启动docker-compose即可

### How to use
在已部署server端的前提下，client可直接单独部署作为节点，每个节点开放哪些服务可控
- 当前节点开放哪些服务由config.ini决定
- xray/domaininfo不需要通过config.ini单独控制
    - 默认开启了fileleak/rad/jsfinder即会开启xray
    - 默认所有客户端开启domaininfo
```
# 1. 更改docker-compose.yml中redis/amqp地址
cd gosint/client
sed -i 's/8.8.8.8/your_server_ip/g' docker-compose.yml

# 2. 启动docker
docker-compose up -d
```

### config files
```
./config.yaml
subdomain_scan/subfinder/tools/config.yaml
subdomain_scan/xray_subdomain/tools/config.yaml
vuln_scan/nuclei/tools/config.yaml
```
### dicts file
```
vuln_scan/fileleak/tools/dicts/file_top_100.txt
vuln_scan/fileleak/tools/dicts/file_top_2000.txt
vuln_scan/fileleak/tools/dicts/file_top_8000.txt
port_scan/naabu/tools/portfile_top10.txt
port_scan/naabu/tools/portfile_top100.txt
port_scan/naabu/tools/portfile_top1000.txt
port_scan/naabu/tools/portfile_all.txt
```