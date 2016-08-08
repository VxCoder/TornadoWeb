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
                self.Return(False)
            
            role_purview = yield self.get_role_purview()
            
            if(not role_purview):
                self.Return(False)
            
            if(role_id not in role_purview):
                self.Return(False)
            
            if(module not in role_purview[role_id]):
                self.Return(False)
            
            result = bool(HttpMethod[method] & role_purview[role_id][module])
            
            self.Return(result)
    
    @coroutine
    def get_role_purview(self):
        
        with catch_error():
            
            ckey = self._mc.key(r'role_purview')
            cval = yield self.get_cache(ckey)
            
            if(cval is not None):
                self.Return(cval)
            
            records = yield self._dbs.select(r'rbac_role')
            
            if(records is None):
                self.Return()
            
            role_infos = {}
            
            for row in records:
                role_infos[row[r'id']] = {}
            
            records = yield self._dbs.select(r'rbac_purview')
            
            if(records):
                for row in records:
                    if(row[r'role'] in role_infos):
                        role_infos[row[r'role']][row[r'module']] = row[r'purview']
            
            yield self.set_cache(ckey, role_infos)
            
            self.Return(role_infos)

