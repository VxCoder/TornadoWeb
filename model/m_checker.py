# -*- coding: utf-8 -*-

from tornado.log import app_log
from tornado.gen import coroutine, Return


@coroutine
def auto_login(request):
    
    app_log.info(r'I am request checker')
    
    raise Return(True)


def logger(request):
    
    app_log.info(r'I am request finisher')

