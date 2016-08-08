FROM python:3.5

MAINTAINER wsb <wsb310@gmail.com>

RUN echo "Asia/Shanghai" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

RUN pip install pillow
RUN pip install cryptography
RUN pip install python-gettext
RUN pip install Sphinx
