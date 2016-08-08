FROM mysql:5.7

MAINTAINER wsb <wsb310@gmail.com>

RUN apt-get update
RUN apt-get install -y cron

RUN echo "Asia/Shanghai" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
