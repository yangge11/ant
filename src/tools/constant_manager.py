#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/10/25 15:24
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : constant_manager.py
# @Software: PyCharm
# @ToUse  : 控制常量值不可修改


class Const(object):
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError, "Can't change const value!"
        if not name.isupper():
            raise self.ConstCaseError, 'const "%s" is not all letters are capitalized' % name
        self.__dict__[name] = value


import sys

sys.modules[__name__] = Const()
