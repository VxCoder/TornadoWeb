# -*- coding: utf-8 -*-

import config

from tornado.gen import coroutine

from util.decorator import singleton, catch_error

from ._base import BaseModel


@singleton
class TuringClient(BaseModel):
    
    def __init__(self):
        
        super().__init__()
        
        self._api_url = r'http://www.tuling123.com/openapi/api'
        self._api_key = config.Static.TuringApiKey
    
    @coroutine
    def __query(self, url, **params):
        
        result = None
        
        with catch_error():
            
            response = yield self.fetch_url(r''.join([self._api_url, url]), params)
            
            if(response):
                result = self.json_decode(response)
            
        self.Return(result)
    
    @coroutine
    def chat(self, userid, info):
        
        aip_url = r''
        
        params = {r'userid':userid, r'info':info}
        
        response = yield self.__query(aip_url, **params)
        
        if(r'text' in response):
            self.Return(response[r'text'])
        elif(r'code' in response):
            self.Return(r'error {0}'.format(response[r'code']))

