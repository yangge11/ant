#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/14 15:10
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : file_manager.py
# @Software: PyCharm
# @ToUse  :
import os


def get_file_size(file_absolute_path):
    return os.path.getsize(file_absolute_path)


def exist_file(file_absolute_path):
    return os.path.exists(file_absolute_path)


def del_file(file_absolute_path):
    return os.remove(file_absolute_path)
