FROM python:3.8-alpine

LABEL maintainer="_lin9e <lin9e@qq.com>"

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
    && apk --no-cache add ca-certificates openssl musl-dev \
    mariadb-dev build-base \
    g++ bash make gcc py3-lxml \
    libffi-dev libevent-dev python3-dev cairo-dev \
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev \
    linux-headers pcre-dev libcap libcap-dev libpcap libpcap-dev \
    nmap libxml2 libxml2-dev libxslt-dev \
    && rm -rf /var/cache/apk/*

# timezone
RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone 

RUN mkdir /lib64 && ln -s /lib/libc.musl-x86_64.so.1 /lib64/ld-linux-x86-64.so.2 && ln -s /usr/lib/libpcap.so /usr/lib/libpcap.so.0.8

RUN mkdir /app
WORKDIR /app

COPY ./thirdparty/chromium-91.0.4472.164-r0.apk /tmp
RUN apk add --allow-untrusted /tmp/chromium-91.0.4472.164-r0.apk

ADD requirements.txt /app/requirements.txt
RUN python -m pip install -r requirements.txt -i https://pypi.douban.com/simple
ADD config.ini /config.ini
ADD docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# install ca.crt
COPY ./vuln_scan/rad2xray/tools/ca.crt /usr/local/share/ca-certificates/xray.crt
RUN update-ca-certificates

ENTRYPOINT [ "/docker-entrypoint.sh"]