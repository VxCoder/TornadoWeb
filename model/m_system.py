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
            
            records1 = (yield self._dbm.query(r'show processlist')).fetchall()
            records2 = (yield self._dbs.query(r'show processlist')).fetchall()
            
            db_live = (len(records1) > 0) or (len(records2) > 0)
        
        with catch_error():
            
            cache = self.get_cache_client()
            
            ckey = r'system_checkup'
            cval = self.timestamp()
            
            yield cache.set(ckey, cval)
            
            mc_live = (cval == (yield cache.get(ckey)))
        
        return db_live and mc_live

