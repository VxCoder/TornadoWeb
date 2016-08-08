# -*- coding: utf-8 -*-

import config

from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import url_concat

from util.util import Utils
from util.cache import MCache, MLock
from util.database import MySQLPool
from util.decorator import catch_error


class BaseModel(Utils):
    
    def __init__(self):
        
        # 数据缓存
        self._mc = MCache()
        
        # 数据连接池
        self._dbm = MySQLPool().master()
        self._dbs = MySQLPool().slave()
    
    def __del__(self):
        
        # 数据缓存
        self._mc = None
        
        # 数据连接池
        self._dbm = None
        self._dbs = None
    
    @coroutine
    def fetch_url(self, url, params=None, method=r'GET', headers=None, body=None):
        
        if(params):
            url = url_concat(url, params)
        
        result = None
        
        with catch_error():
            
            client = AsyncHTTPClient()
            
            response = yield client.fetch(HTTPRequest(url, method, headers, body))
            
            result = self.utf8(response.body)
        
        self.Return(result)
    
    @staticmethod
    def allocate_lock(*args):
        
        return MLock(*args)
    
    def cache_key(self, *keys):
        
        return self._mc.key(*keys)
    
    @coroutine
    def get_cache(self, key):
        
        result = yield self._mc.get(key)
        
        self.Return(result)
    
    @coroutine
    def get_multi_cache(self, *keys):
        
        result = yield self._mc.mget(*keys)
        
        self.Return(result)
    
    @coroutine
    def set_cache(self, key, val, time=0):
        
        if(time == 0):
            time = config.Static.RedisExpires
        
        result = yield self._mc.set(key, val, time)
    
    @coroutine
    def set_multi_cache(self, **mapping):
        
        result = yield self._mc.mset(**mapping)
        
        self.Return(result)
    
    @coroutine
    def del_cache(self, pattern=r'*'):
        
        keys = yield self._mc.keys(pattern)
        
        if(keys):
            
            result = yield self._mc.delete(*keys)
            
            self.Return(result)
        
        else:
            
            self.Return(True)

