# -*- coding: utf-8 -*-

from tornado.log import app_log


class Ignore(Exception):
    
    def __init__(self, msg=None):
        
        if(msg):
            app_log.debug(msg)


class Dict(dict):
    
    def __init__(self):
        
        dict.__init__(self)
    
    def __getattr__(self, key):
        
        return self.__getitem__(key)
    
    def __setattr__(self, key, val):
        
        self.__setitem__(key, val)
    
    def __getitem__(self, key):
        
        return super().__getitem__(key)
    
    def __setitem__(self, key, val):
        
        super().__setitem__(key, val)
    
    def __delattr__(self, key):
        
        self.__delitem__(key)
    
    def __delitem__(self, key):
        
        super().__delitem__(key)


class Const(dict):
    
    class ConstError(TypeError): pass
    
    def __init__(self):
        
        dict.__init__(self)
    
    def __getattr__(self, key):
        
        return self.__getitem__(key)
    
    def __setattr__(self, key, val):
        
        self.__setitem__(key, val)
    
    def __getitem__(self, key):
        
        return super().__getitem__(key)
    
    def __setitem__(self, key, val):
        
        if key in self:
            raise self.ConstError()
        else:
            super().__setitem__(key, val)
    
    def __delattr__(self, key):
        
        self.__delitem__(key)
    
    def __delitem__(self, key):
        
        raise self.ConstError()

