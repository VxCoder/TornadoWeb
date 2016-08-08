# -*- coding: utf-8 -*-

from io import BytesIO

from qrcode import QRCode

from tornado.gen import coroutine, Return

from util.web import SocketBaseHandler, RequestSessHandler, RequestRbacHandler

from model import m_checker

from model.m_system import SystemModel
from model.m_account import AccountModel
from model.m_baidu_map import BaiduMapClient


class default(RequestSessHandler):
    
    _checkers = [m_checker.auto_login]
    
    _finishers = [m_checker.logger]
    
    @coroutine
    def get(self):
        
        return self.render(r'home/default.html', info=self.current_user)
    
    @coroutine
    def head(self):
        
        m_system = SystemModel()
        
        if(yield m_system.checkup()):
            return self.write(self.client_ip)
        else:
            return self.send_error(503)


class login(RequestRbacHandler):
    
    @coroutine
    def rbac_auth(self):
        
        raise Return(True)
    
    @coroutine
    def get(self):
        
        m_account = AccountModel()
        
        info = yield m_account.login(r'administrator', r'19830310')
        
        if(info):
            self.rbac_role = info[r'rbac_role']
        
        return self.write_json(info)


class qrcode(RequestRbacHandler):

    @coroutine
    def get(self):
        
        self.set_header(r'Content-Type', r'image/png')
        
        stream = BytesIO()
        
        code = QRCode()
        
        code.add_data(self.get_argument(r'data', r''))
        
        code.make_image().save(stream)
        
        return self.finish(stream.getvalue())


class captcha(RequestRbacHandler):

    @coroutine
    def get(self):
        
        return self.generate_captcha(120, 50)


class geocoder(RequestRbacHandler):

    @coroutine
    def get(self):
        
        client = BaiduMapClient()
        
        result = yield client.geocoder(r'杭州市萧山区崇化小区')
        
        return self.finish(result)


class socket(SocketBaseHandler):

    @coroutine
    def open(self):
        
        self.debug(r'WebSocket opened')

    @coroutine
    def on_message(self):
        
        self.debug(r'WebSocket message')

    @coroutine
    def on_close(self):
        
        self.debug(r'WebSocket closed')

