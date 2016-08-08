# -*- coding: utf-8 -*-

import time

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
            
            ckey = r'system_checkup'
            cval = self.timestamp()
            
            yield self.set_cache(ckey, cval)
            
            mc_live = (cval == (yield self.get_cache(ckey)))
        
        return db_live and mc_live

