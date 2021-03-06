# -*- coding: utf-8 -*-

import config

from tornado.gen import coroutine, Task
from tornado.concurrent import Future
from tornado_redis import Client, ConnectionPool

from .decorator import singleton
from .util import Utils


@singleton
class MCachePool():
    
    def __init__(self):
        
        self.__conn_pool = ConnectionPool(host=config.Static.RedisHost[0], port=config.Static.RedisHost[1], max_connections=config.Static.RedisMaxConn)
    
    def __del__(self):
        
        self.__conn_pool = None
    
    def get_client(self, selected_db=0):
        
        return MCache(password=config.Static.RedisPasswd, selected_db=selected_db, connection_pool=self.__conn_pool)


class MCache(Utils):
    
    def __init__(self, *args, **kwargs):
        
        self.__client = Client(*args, **kwargs)
        
        self.__expire = config.Static.RedisExpires
    
    def __del__(self):
            
        self.__client = None
    
    def key(self, key, *args, **kwargs):
        
        if(not args or not kwargs):
            return str(key)
        
        keys = []
        
        if(args):
            keys.extend(args)
        
        if(kwargs):
            keys.extend(sorted(kwargs.items(), key=lambda x:x[0]))
        
        keys = self.md5(r'_'.join(str(arg) for arg in args))
        
        return r'_'.join([str(key), keys])
    
    @coroutine
    def touch(self, key, expire=0):
        
        result = yield Task(self.__client.expire, key, expire)
        
        return result
    
    @coroutine
    def has(self, key):
        
        result = yield Task(self.__client.exists, key)
        
        return result
    
    @coroutine
    def get(self, key):
        
        result = yield Task(self.__client.get, key)
        
        if(result is not None):
            result = self.pickle_loads(result)
        
        return result
    
    @coroutine
    def mget(self, *keys):
        
        if(not keys):
            return None
        
        result = yield Task(self.__client.mget, keys)
        
        if(result):
            for key, val in enumerate(result):
                if(val is not None):
                    result[key] = self.pickle_loads(val)
        
        return result
    
    @coroutine
    def set(self, key, val, expire=0):
        
        if(val is None):
            return False
        
        if(expire <= 0):
            expire = self.__expire
        
        val = self.pickle_dumps(val)
        
        result = yield Task(self.__client.set, key, val, expire)
        
        return result
    
    @coroutine
    def setnx(self, key, val, expire=0):
        
        if(val is None):
            return False
        
        if(expire <= 0):
            expire = self.__expire
        
        val = self.pickle_dumps(val)
        
        result = yield Task(self.__client.set, key, val, expire, only_if_not_exists=True)
        
        return result
    
    @coroutine
    def setxx(self, key, val, expire=0):
        
        if(val is None):
            return False
        
        if(expire <= 0):
            expire = self.__expire
        
        val = self.pickle_dumps(val)
        
        result = yield Task(self.__client.set, key, val, expire, only_if_exists=True)
        
        return result
    
    @coroutine
    def mset(self, **mapping):
        
        if(not mapping):
            return False
        
        for key, val in mapping.items():
            mapping[key] = self.pickle_dumps(val)
        
        result = yield Task(self.__client.mset, mapping)
        
        return result
    
    @coroutine
    def msetnx(self, **mapping):
        
        if(not mapping):
            return False
        
        for key, val in mapping.items():
            mapping[key] = self.pickle_dumps(val)
        
        result = yield Task(self.__client.msetnx, mapping)
        
        return result
    
    @coroutine
    def delete(self, *keys):
        
        result = yield Task(self.__client.delete, *keys)
        
        return result
    
    @coroutine
    def keys(self, pattern=r'*'):
        
        result = yield Task(self.__client.keys, pattern)
        
        return result


class MLock():
    
    def __init__(self, *args):
        
        self._cache = MCachePool().get_client()
        
        self._lock_tag = self._cache.key(r'threading_lock', args)
        
        self._valid = False
    
    @coroutine
    def acquire(self, expire=60):
        
        now_time = self._cache.timestamp()
        
        self._valid = yield self._cache.setnx(self._lock_tag, now_time, expire)
        
        while(not self._valid):
            self._valid = yield self._cache.setnx(self._lock_tag, now_time, expire)
    
    @coroutine
    def release(self):
        
        if(self._valid):
        
            self._valid = False
            
            if(self._cache):
                yield self._cache.delete(self._lock_tag)
            
        self._cache = None
        
        self._lock_tag = None
    
    def __enter__(self):
        
        return self
    
    def __exit__(self, *args):
        
        self.release()
    
    def __del__(self):
        
        self.release()


def FuncCache(expire=0):
    
    if(expire <= 0):
        expire = config.Static.FuncCacheExpires
    
    def _wrapper(func):
        
        def __wrapper(*args , **kwargs):
            
            cache = MCachePool().get_client()
            
            ckey = cache.key(func, *args, **kwargs)
            
            result = yield cache.get(ckey)
            
            if(result is None):
                
                result = func(*args, **kwargs)
                
                if(isinstance(result, Future)):
                    result = yield result
                
                yield cache.set(ckey, result, expire)
            
            return result
        
        return coroutine(__wrapper)
    
    return _wrapper


func_cache = FuncCache

