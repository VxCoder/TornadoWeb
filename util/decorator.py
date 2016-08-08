# -*- coding: utf-8 -*-

import traceback

from contextlib import contextmanager

from tornado.log import app_log
from tornado.gen import Return

from .struct import Ignore


def singleton(cls):
    
    _instances = {}
    
    def _singleton(*args, **kwargs):
        
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        
        return _instances[cls]
    
    return _singleton


@contextmanager
def catch_error(callback = None, *args, **kwargs):
    
    try:
        
        yield
        
    except Return as err:
        
        raise err
        
    except Ignore as err:
        
        pass
    
    except Exception as err:
        
        app_log.error(str(err))
        
        app_log.error(traceback.format_exc())
        
    finally:
        
        if(callback):
            callback(*args, **kwargs)

