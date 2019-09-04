# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/6/12 14:34

""" 包初始化脚本 """

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import base_dir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
import flask_whooshalchemyplus
from flask_mail import Mail
from .momentjs import momentjs
from flask_babel import Babel, lazy_gettext


app = Flask(__name__)
# 读取配置文件
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'main.login'
# 多语言处理Flask自带的登录提醒
lm.login_message = lazy_gettext('请登录后访问本页.')

flask_whooshalchemyplus.init_app(app)

from app.leaf.leaf_models import Post
flask_whooshalchemyplus.whoosh_index(app, Post)
from app.book.book_models import Book
flask_whooshalchemyplus.whoosh_index(app, Book)

mail = Mail(app)

# 将封装类与jinja2绑定
app.jinja_env.globals['momentjs'] = momentjs

# 国际化支持
babel = Babel(app)

from app.main import views, models
from app.leaf import leaf_views, leaf_models
from app.book import book_views, book_models

# 使用邮件发生服务器异常信息
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler(MAIL_SERVER, MAIL_PORT, 'rjguanwen001@163.com', ADMINS, 'Ginkgo 异常', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
    # SMTP调试服务器，使用命令行窗口伪造邮箱服务器
    # python - m smtpd - n - c DebuggingServer localhost: 25

# 使用日志记录服务器异常信息
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    # 日志文件的大小限制在1兆，我们将保留最后10个日志文件作为备份
    log_path = os.path.join(os.path.join(base_dir, 'tmp'), 'Ginkgo.log')
    file_handler = RotatingFileHandler(log_path, 'a', 1*1024*1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('Ginkgo startup')
