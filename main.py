# -*- coding: utf-8 -*-

import config, router, service, platform, signal

from tornado.web import Application
from tornado.log import app_log
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.process import cpu_count, fork_processes
from tornado.netutil import bind_sockets
from tornado.httpserver import HTTPServer

from util.template import Jinja2Loader


def startup():
    
    define(r'port', 80, int, r'Server listen port')
    define(r'service', False, bool, r'Open Scheduled Tasks')
    
    options.parse_command_line()
    
    if(config.Static.Debug):
        options.parse_command_line([__file__, r'--service=true', r'--logging=debug'])
    
    settings = {
                r'handlers': router.urls,
                r'static_path': r'static',
                r'template_loader': Jinja2Loader(r'view'),
                r'debug': config.Static.Debug,
                r'gzip': config.Static.GZip,
                r'cookie_secret': config.Static.Secret,
                }
    
    sockets = bind_sockets(options.port)
    
    task_id = 0
    
    if(platform.system() == r'Linux'):
        task_id = fork_processes(cpu_count())
    
    server = HTTPServer(Application(**settings))
    
    server.add_sockets(sockets)
    
    if(task_id == 0 and options.service):
        service.start()
    
    signal.signal(signal.SIGINT, lambda *args : shutdown(server))
    signal.signal(signal.SIGTERM, lambda *args : shutdown(server))
    
    app_log.info(r'Startup http server No.{0}'.format(task_id))
    
    IOLoop.instance().start()


def shutdown(server):
    
    service.stop()
    
    server.stop()
    
    IOLoop.instance().stop()
    
    app_log.info(r'Shutdown http server')


if __name__ == r'__main__':
    
    startup()

