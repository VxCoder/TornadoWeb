# -*- coding: utf-8 -*-

import config, oss2

from tornado.gen import coroutine

from util.decorator import singleton, catch_error

from ._base import BaseModel


@singleton
class AliyunOssClient(BaseModel):
    
    def __init__(self):
        
        super().__init__()
        
        self._auth = oss2.Auth(config.Static.AliyunAccessKey, config.Static.AliyunSecretKey)
        self._bucket = oss2.Bucket(self._auth, config.Static.AliyunOssServer, config.Static.AliyunOssBucket)
    
    @coroutine
    def get_sign_url(self, filename):
        
        result = None
        
        with catch_error():
            
            result = self._bucket.sign_url(r'GET', filename, 3600)
        
        return result
    
    @coroutine
    def put_file(self, filename, filedata):
        
        result = False
        
        with catch_error():
            
            response = self._bucket.put_object(filename, filedata)
            
            self.debug(response)
            
            result = (response.status == 200)
        
        return result
    
    @coroutine
    def del_file(self, filename):
        
        result = False
        
        with catch_error():
            
            response = self._bucket.delete_object(filename)
            
            self.debug(response)
            
            result = (response.status == 204)
            
        return result

