# -*- coding: utf-8 -*-

import math, time, config

from crontab import CronTab
from threadpool import ThreadPool, WorkRequest

from tornado.log import app_log
from tornado.ioloop import IOLoop, PeriodicCallback

from .decorator import singleton


@singleton
class AsyncTasks(ThreadPool):
    
    def __init__(self):
        
        ThreadPool.__init__(self, config.Static.ThreadPool, config.Static.ThreadPoolLimit)
        
        self._schedule = {}
    
    def addWorker(self, callback, *args, **kwargs):
        """添加线程worker，使用Python的线程池，不依赖Tornado的异步模式
        """
        
        request = WorkRequest(callback, args, kwargs)
        
        self.putRequest(request)
        
    def addTimeout(self, deadline, callback, *args, **kwargs):
        """添加协程worker，仅为Tornado的add_timeout的封装，callback需要使用gen.engine修饰
        """
        
        return IOLoop.current().add_timeout(math.ceil(time.time() + deadline), callback, *args, **kwargs)
        
    def removeTimeout(self, timeout):
        """移除协程worker，仅为Tornado的remove_timeout的封装
        """
        
        return IOLoop.current().remove_timeout(timeout)
    
    def addSchedule(self, crontab, callback):
        """添加计划任务，依赖Tornado的异步模式，不能保证精确的执行时间，callback需要使用gen.engine修饰
        """
        
        if(callback in self._schedule):
            return None
        
        task = self._schedule[callback] = Task(crontab, callback)
        
        task.start()
    
    def removeSchedule(self, callback):
        """移除计划任务
        """
        
        if(callback in self._schedule):
            
            self._schedule[callback].stop()
            
            del self._schedule[callback]
    
    def removeAllSchedule(self):
        """移除计划任务
        """
        
        for task in self._schedule.values():
            task.stop()
        
        self._schedule.clear()


class Task(CronTab, PeriodicCallback):
    
    def __init__(self, crontab, callback):
        
        CronTab.__init__(self, crontab)
        
        PeriodicCallback.__init__(self, callback, self.next(), IOLoop.current())
    
    def next(self):
        
        return math.ceil(CronTab.next(self)) * 1000
    
    def _run(self):
        
        app_log.info(r'Run task {0:s}'.format(self.callback.__name__))
        
        return PeriodicCallback._run(self)
    
    def _schedule_next(self):
        
        self.callback_time = self.next()
        
        PeriodicCallback._schedule_next(self)

