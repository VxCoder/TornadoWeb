# -*- coding: utf-8 -*-

from util.struct import Const


##################################################

Static = Const()

Static.Debug = True

Static.GZip = True

Static.Secret = r'02b6d796814c353a1f0370a416018016'

Static.SessionExpires = 1800

Static.AccessControlAllowOrigin = (r'*',)

Static.FuncCacheExpires = 10

##################################################
# 线程

Static.ThreadPool = 5
Static.ThreadPoolLimit = 10

##################################################
# 数据库

Static.MySqlMaster = (r'localhost', 3306)
Static.MySqlSlave = (r'localhost', 3306)
Static.MySqlName = r'demo'
Static.MySqlUser = r'root'
Static.MySqlPasswd = r''
Static.MySqlMaxIdleConn = 32
Static.MySqlMaxOpenConn = 128

Static.RedisHost = (r'localhost', 6379)
Static.RedisBases = 16
Static.RedisPasswd = None
Static.RedisMaxConn = 128
Static.RedisExpires = 3600

##################################################
# 第三方接口

# 百度地图
Static.BaiduMapAK = r'60ZDdws6u4jZGVzmfDsw2DoZ'

# 图灵机器人
Static.TuringApiKey = r'3bbac767ada27e4759468b8514efb766'

# 阿里云
Static.AliyunAccessKey = r'eWFHtAZhzxaDUbzk'
Static.AliyunSecretKey = r'eG7IVNEQ0Bhea2tPzwoiHawSeuaPyj'

Static.AliyunOssServer = r'oss-cn-hangzhou.aliyuncs.com'
Static.AliyunOssBucket = r'wsb310'

##################################################

