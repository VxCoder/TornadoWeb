# -*- coding: utf-8 -*-

from tornado.gen import coroutine

from util.decorator import singleton, catch_error

from ._base import BaseModel


@singleton
class AccountModel(BaseModel):
    
    @coroutine
    def search(self):
        
        result = None
        
        with catch_error():
            
            cache = self.get_cache_client()
            
            ckey = cache.key(r'account_infos')
            cval = yield cache.get(ckey)
            
            if(cval is None):
                
                records = yield self._dbs.select(r'account', limit=100)
                
                if(records):
                    
                    cval = [dict(val) for val in records]
                    
                    yield cache.set(ckey, cval)
            
            result = cval
            
        return result
    
    @coroutine
    def register(self, username, password):
        
        result = None
        
        with (yield self._dbm.begin()) as trx:
            
            records = yield trx.where(r'account', username=username, rowlock=True)
            
            if(records):
                self.Break()
            
            fields = {
                      r'username': username,
                      r'password': self.md5(password),
                      r'purview': 0,
                      }
            
            fields[r'id'] = trx.insert(r'account', **fields)
            
            if(fields[r'id']):
                
                yield trx.commit()
                
                result = fields
        
        return result

    @coroutine
    def login(self, username, password):
        
        result = None
        
        with catch_error():
            
            record = yield self._dbs.where(r'account', username=username)
            
            if(not record):
                self.Break()
            
            info = dict(record)
            
            if(info[r'password'] == self.md5(password)):
                result = info
        
        return result

