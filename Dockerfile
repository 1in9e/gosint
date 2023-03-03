FROM python:3.8-alpine3.13

LABEL maintainer="_lin9e <lin9e@qq.com>"

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
    && apk update \
    && apk add mariadb-dev build-base \
    g++ bash make gcc\
    libffi-dev python3-dev \
    supervisor

RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone

RUN mkdir /app
WORKDIR /app

ADD thirdparty/requirements.txt /app
RUN pip install -U pip -i https://pypi.douban.com/simple
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple

COPY thirdparty/simplepro-3.3.2.tar.gz /app
RUN pip install simplepro-3.3.2.tar.gz -i https://pypi.douban.com/simple

ADD docker-entrypoint.sh /docker-entrypoint.sh
ADD ./thirdparty/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /docker-entrypoint.sh
RUN chmod +x /wait-for-it.sh
WORKDIR /app
ENTRYPOINT [ "/docker-entrypoint.sh"]
