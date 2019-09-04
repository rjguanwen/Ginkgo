# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/6/12 16:01

""" 表单脚本 """

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length
from .models import User


class LoginForm(FlaskForm):
    """ 登录表单 """
    user_name = StringField('user_name', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class UserEditForm(FlaskForm):
    """ 用户信息编辑表单 """
    nickname = StringField('nickname', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        """ 验证昵称是否重复 """
        if not FlaskForm.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            # 如果用户输入的昵称不符合要求
            self.nickname.errors.append('昵称只能由字母,数字,点和下划线组成,请重新输入!')
            return False
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('该昵称已存在，请重新输入！')
            return False
        return True
