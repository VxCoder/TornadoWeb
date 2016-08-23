# -*- coding: utf-8 -*-

from tornado.gen import coroutine

from util.decorator import singleton, catch_error

from ._base import BaseModel


@singleton
class SystemModel(BaseModel):
    
    @coroutine
    def checkup(self):
        
        db_live = False
        mc_live = False
        
        with catch_error():
            
            db_client1 = yield self.get_db_client(True)
            db_client2 = yield self.get_db_client(False)
            
            records1 = (yield db_client1.query(r'show processlist')).fetchall()
            records2 = (yield db_client2.query(r'show processlist')).fetchall()
            
            db_live = (len(records1) > 0) or (len(records2) > 0)
        
        with catch_error():
            
            cache = self.get_cache_client()
            
            ckey = r'system_checkup'
            cval = self.timestamp()
            
            yield cache.set(ckey, cval)
            
            mc_live = (cval == (yield cache.get(ckey)))
        
        return db_live and mc_live

