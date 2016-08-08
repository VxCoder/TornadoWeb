FROM nginx:1.10

MAINTAINER wsb <wsb310@gmail.com>

RUN apt-get update
RUN apt-get install -y cron curl

RUN echo "Asia/Shanghai" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata
