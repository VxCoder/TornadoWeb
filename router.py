# -*- coding: utf-8 -*-

from tornado.web import StaticFileHandler

from controller import *


urls = [
    
    (r'/static/(.*)',                                                StaticFileHandler),
    
    (r'/?',                                                          home.default),
    
    (r'/login/?',                                                    home.login),
    
    (r'/qrcode/?',                                                   home.qrcode),
    (r'/captcha/?',                                                  home.captcha),
    
    (r'/geocoder/?',                                                 home.geocoder),
    
    (r'/socket/?',                                                   home.socket),
    
]

