# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/6/12 15:57

""" 配置文件 """

import os


# 激活跨站点请求伪造保护
CSRF_ENABLED = True
# SECRET_KEY 配置仅仅当 CSRF 激活的时候才需要，它是用来建立一个加密的令牌，用于验证一个表单
SECRET_KEY = 'Iamsecret3232998765'

base_dir = os.path.abspath(os.path.dirname(__file__))

# 数据库文件的路径
SQLALCHEMY_DATABASE_URI ='sqlite:///' + os.path.join(base_dir, 'ginkgo.db')
# SQLAlchemy-migrate 数据文件存储路径
SQLALCHEMY_MIGRATE_REPO = os.path.join(base_dir, 'db_repository')

# 邮件服务器配置
MAIL_SERVER = 'smtp.163.com'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = 'rjguanwen001'
MAIL_PASSWORD = os.environ.get('MAIL_P')

ADMINS = ['rjguanwen001@163.com']

# 每页文章条数
POSTS_PER_PAGE = 10

# 设定全文检索相关配置
WHOOSH_BASE = os.path.join(base_dir, 'search.db')
MAX_SEARCH_RESULTS = 50

# 国际化多语言配置
LANGUAGES = {
    'en': 'English',
    'zh': 'Chinese'
}
BABEL_DEFAULT_LOCALE = 'zh'

# 百度翻译相关账号信息
BAIDU_TRANSLATOR_CLIENT_ID = '20180627000180833'
BAIDU_TRANSLATOR_CLIENT_SECRET = 'VII99D90npp78BNUdGBw'

# 数据库执行时间监控与预警配置
SQLALCHEMY_RECORD_QUERIES = True
DATABASE_QUERY_TIMEOUT = 0.5

# 微信小程序AppId及AppSecret
WECHAT_APP_ID = 'wx98307b2ea1d5ba6a'
WECHAT_APP_SECRET = '6170b5f6a84a70484a379650c3bb0aa2'

# 数据聚合，ISBN查询key
JUHE_ISBN_KEY = '9eb879804a42d8bfe777469e1e289bdc'

# 每页书籍数量
BOOK_PER_PAGE = 10
