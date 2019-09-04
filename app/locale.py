# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/7/28 11:37

"""  """
from app import babel
from flask import request
from config import LANGUAGES


@babel.localeselector
def get_locale():
    # 返回最匹配浏览器发送的request请求中指定的语言
    # print(request.accept_languages.best_match(LANGUAGES.keys()))
    return request.accept_languages.best_match(LANGUAGES.keys())
    # return 'en'