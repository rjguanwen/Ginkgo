# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/6/12 16:01

""" 表单脚本 """

from flask_wtf import FlaskForm
from wtforms import StringField, RadioField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    post = StringField('post', validators=[DataRequired()])


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])
    # search_type = RadioField('search_type', choices=[('post_s', '文章'), ('book_s', '书籍')],
    #                               validators=[DataRequired()])
