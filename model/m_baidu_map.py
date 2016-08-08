# -*- coding: utf-8 -*-

import config

from tornado.gen import coroutine

from util.decorator import singleton, catch_error

from ._base import BaseModel


@singleton
class BaiduMapClient(BaseModel):
    """目前支持的坐标类型包括：bd09ll（百度经纬度坐标）、bd09mc（百度米制坐标）、gcj02ll（国测局经纬度坐标）、wgs84ll（ GPS经纬度）
    """
    
    def __init__(self):
        
        super().__init__()
        
        self._api_url = r'http://api.map.baidu.com'
        self._api_key = config.Static.BaiduMapAK
    
    @coroutine
    def __query(self, url, **params):
        
        args = [str(val) for val in sorted(params.items(), key=lambda x:x[0])]
        
        ckey = self.cache_key(r'baidu_map', url, *args)
        cval = yield self.get_cache(ckey)
        
        if(cval is None):
            
            params[r'ak'] = self._api_key
            params[r'output'] = r'json'
            
            with catch_error():
                
                response = yield self.fetch_url(r''.join([self._api_url, url]), params)
                
                if(response):
                    cval = self.json_decode(response)
                    self.set_cache(ckey, cval)
            
        self.Return(cval)
    
    @coroutine
    def geocoder(self, addr, coor=r'bd09ll', pois=False):
        """地址解析
        """
        
        aip_url = r'/geocoder/v2/'
        
        params = {}
        
        style = type(addr)
        
        if(style is str):
            params[r'address'] = addr
        elif(style in (list,tuple,)):
            params[r'location'] = r','.join(str(val) for val in addr)
        
        params[r'coordtype'] = coor
        params[r'pois'] = 1 if pois else 0
        
        response = yield self.__query(aip_url, **params)
        
        self.Return(response)
    
    @coroutine
    def ip(self, addr, coor=r'bd09ll'):
        """IP定位
        """
        
        aip_url = r'/location/ip'
        
        params = {r'ip':addr, r'coor':coor}
        
        response = yield self.__query(aip_url, **params)
        
        self.Return(response)

