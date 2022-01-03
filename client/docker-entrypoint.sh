#!/bin/bash

set -ex
source config.ini

# subdomain_scan:subfinder
if $subfinder; then
	cd /app/subdomain_scan/subfinder
	nohup celery -A subfinder worker -l info -c 1 -Q subfinder -n subfinder_$RANDOM --logfile=/app/logs/subfinder_celery.log >/dev/null 2>&1 &
fi

# subdomain_scan:ksubdomain
if $ksubdomain; then
	cd /app/subdomain_scan/ksubdomain
	nohup celery -A ksubdomain worker -l info -c 1 -Q ksubdomain -n ksubdomain_$RANDOM --logfile=/app/logs/ksubdomain_celery.log >/dev/null 2>&1 &
fi

# subdomain_scan:xray_subdomain
if $xray_subdomain; then
	cd /app/subdomain_scan/xray_subdomain
	nohup celery -A xray_subdomain worker -l info -c 1 -Q xray_subdomain -n xray_subdomain_$RANDOM --logfile=/app/logs/subdomain_xray_celery.log >/dev/null 2>&1 &
fi

# subdomain_scan:certip
if $certip; then
	cd /app/subdomain_scan/certip
	nohup celery -A certip worker -l info -Q certip -c 1 -n certip_$RANDOM --logfile=/app/logs/certip_celery.log >/dev/null 2>&1 &
fi

# httpx
if $httpx; then
	cd /app/httpx
	nohup celery -A httpx worker -l info -Q httpx -c 1 -n httpx_$RANDOM --logfile=/app/logs/httpx_celery.log >/dev/null 2>&1 &
fi

# port_scan:naabu
if $naabu; then
	cd /app/port_scan/naabu
	nohup celery -A naabu worker -l info -Q naabu -n naabu_$RANDOM --logfile=/app/logs/naabu_celery.log >/dev/null 2>&1 &
fi

# port_scan:port_api
if $port_api; then
	cd /app/port_scan/port_api
	nohup celery -A port_api worker -l info -Q port_api -c 1 -n port_api_$RANDOM --logfile=/app/logs/port_api_celery.log >/dev/null 2>&1 &
fi

# vuln_scan:fileleak
if $fileleak; then
	cd /app/vuln_scan/fileleak
	nohup celery -A fileleak worker -l info -Q fileleak -c 2 -n fileleak_$RANDOM --logfile=/app/logs/fileleak_celery.log >/dev/null 2>&1 &
fi
# vuln_scan:jsfinder
if $jsfinder; then
	cd /app/vuln_scan/jsfinder
	nohup celery -A jsfinder worker -l info -Q jsfinder -n jsfinder_$RANDOM --logfile=/app/logs/jsfinder_celery.log >/dev/null 2>&1 &
fi
# vuln_scan:redfinger
if $redfinger; then
  cd /app/vuln_scan/redfinger
  nohup celery -A redfinger worker -l info -Q redfinger -c 1 -n redfinger_$RANDOM --logfile=/app/logs/redfinger_celery.log >/dev/null 2>&1 &
fi
# vuln_scan:nuclei
if $nuclei; then
	cd /app/vuln_scan/nuclei
	nohup celery -A nuclei worker -l info -Q nuclei -c 1 -n nuclei_$RANDOM --logfile=/app/logs/nuclei_celery.log >/dev/null 2>&1 &
fi

# vuln_scan:rad2xray
if $rad2xray; then
  cd /app/vuln_scan/rad2xray
	nohup celery -A rad2xray worker -l info -Q rad2xray -c 1 -n rad2xray_$RANDOM --logfile=/app/logs/rad2xray_celery.log >/dev/null 2>&1 &
fi

# mkdir logs fixbug: https://github.com/1in9e/gosint/issues/3
#mkdir /app/logs

# vuln_scan: xray passive_scan (jsfinder or  fileleak or rad2xray)
if $rad2xray || $jsfinder || $fileleak; then
  cd /app/vuln_scan/rad2xray/tools/
  nohup ./xray webscan --listen 0.0.0.0:7777 --html-output ./report_$RANDOM.html --webhook-output $SERVER_URL/xray/webhook_a5c3d08371aec44c/ > /app/logs/xray.log &
fi

# domaininfo
cd /app/subdomain_scan/domaininfo
celery -A domaininfo worker -l info -Q domaininfo -n domaininfo_$RANDOM --logfile=/app/logs/domaininfo_celery.log >/dev/null 2>&1