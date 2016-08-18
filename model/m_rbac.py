# -*- coding: utf-8 -*-

from tornado.gen import coroutine

from util.struct import Const
from util.decorator import singleton, catch_error

from ._base import BaseModel


HttpMethod = Const()

HttpMethod.head     = 0x00000001
HttpMethod.get      = 0x00000002
HttpMethod.post     = 0x00000004
HttpMethod.delete   = 0x00000008
HttpMethod.patch    = 0x00000010
HttpMethod.put      = 0x00000020
HttpMethod.options  = 0x00000040


@singleton
class RbacModel(BaseModel):
    
    @coroutine
    def auth(self, role_id, module, method):
        
        with catch_error():
            
            if(method not in HttpMethod):
                return False
            
            role_purview = yield self.get_role_purview()
            
            if(not role_purview):
                return False
            
            if(role_id not in role_purview):
                return False
            
            if(module not in role_purview[role_id]):
                return False
            
            result = bool(HttpMethod[method] & role_purview[role_id][module])
            
            return result
    
    @coroutine
    def get_role_purview(self):
        
        with catch_error():
            
            cache = self.get_cache_client()
            
            ckey = cache.key(r'role_purview')
            cval = yield cache.get(ckey)
            
            if(cval is not None):
                return cval
            
            records = yield self._dbs.select(r'rbac_role')
            
            if(records is None):
                return None
            
            role_infos = {}
            
            for row in records:
                role_infos[row[r'id']] = {}
            
            records = yield self._dbs.select(r'rbac_purview')
            
            if(records):
                for row in records:
                    if(row[r'role'] in role_infos):
                        role_infos[row[r'role']][row[r'module']] = row[r'purview']
            
            yield cache.set(ckey, role_infos)
            
            return role_infos

