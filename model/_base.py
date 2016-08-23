# -*- coding: utf-8 -*-

import config

from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import url_concat

from util.util import Utils
from util.cache import MCachePool, MLock
from util.database import MySQLPool
from util.decorator import catch_error


class BaseModel(Utils):
    
    def __init__(self):
        
        # 数据缓存
        self._mc = MCachePool()
        
        # 数据连接
        self._db = MySQLPool()
    
    def __del__(self):
        
        # 数据缓存
        self._mc = None
        
        # 数据连接
        self._db = None
    
    @staticmethod
    def allocate_lock(*args):
        
        return MLock(*args)
    
    @coroutine
    def fetch_url(self, url, params=None, method=r'GET', headers=None, body=None):
        
        if(params):
            url = url_concat(url, params)
        
        result = None
        
        with catch_error():
            
            client = AsyncHTTPClient()
            
            response = yield client.fetch(HTTPRequest(url, method, headers, body))
            
            result = self.utf8(response.body)
        
        return result
    
    def get_cache_client(self):
        
        class_name = self.md5(self.__class__.__name__)
        
        selected_db = int(class_name, 16) % config.Static.RedisBases
        
        return self._mc.get_client(selected_db)
    
    @coroutine
    def get_db_client(self, readonly):
        
        result = yield self._db.get_client(readonly)
        
        return result
    
    @coroutine
    def get_db_transaction(self):
        
        result = yield self._db.get_transaction()
        
        return result

