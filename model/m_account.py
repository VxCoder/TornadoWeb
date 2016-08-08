# -*- coding: utf-8 -*-

from tornado.gen import coroutine

from util.decorator import singleton, catch_error

from ._base import BaseModel


@singleton
class AccountModel(BaseModel):
    
    @coroutine
    def search(self):
        
        with catch_error():
            
            ckey = self._mc.key(r'account_infos')
            cval = yield self.get_cache(ckey)
            
            if(cval is not None):
                self.Return(cval)
            
            records = yield self._dbs.select(r'account', limit=100)
            
            if(records is None):
                self.Return()
            
            cval = [dict(val) for val in records]
            
            yield self.set_cache(ckey, cval)
            
            self.Return(cval)
    
    @coroutine
    def register(self, username, password):
        
        with (yield self._dbm.begin()) as trx:
            
            records = yield trx.where(r'account', username=username, rowlock=True)
            
            if(records):
                self.Return()
            
            fields = {
                      r'username': username,
                      r'password': self.md5(password),
                      r'purview': 0,
                      }
            
            fields[r'id'] = trx.insert(r'account', **fields)
            
            if(fields[r'id']):
                yield trx.commit()
                self.Return(fields)
            else:
                self.Return()
    
    @coroutine
    def login(self, username, password):
        
        with catch_error():
            
            record = yield self._dbs.where(r'account', username=username)
            
            if(not record):
                self.Return()
            
            info = dict(record)
            
            if(info[r'password'] == self.md5(password)):
                self.Return(info)
            else:
                self.Return()

