#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/21 17:13
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : http_tools.py
# @Software: PyCharm
# @ToUse  : 涉及各类http请求的函数封装
import urllib


def url_decode(url_to_decode):
    # url_decode = urllib.unquote(str(url_to_decode)).decode('utf-8', 'replace').encode('gbk', 'replace')
    url_decode = urllib.unquote(str(url_to_decode))
    return url_decode
