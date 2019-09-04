# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/7/27 20:37

""" 主入口 """

from flask import Flask
from app.main.views import main
from app.leaf.leaf_views import leaf
from app.book.book_views import book
from app import app

app.register_blueprint(main, url_prefix='/')
app.register_blueprint(leaf, url_prefix='/leaf')
app.register_blueprint(book, url_prefix='/book')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
