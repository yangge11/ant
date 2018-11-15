#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/10/17 16:46
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : settings.py
# @Software: PyCharm
# @ToUse  : all settings

# support_sites settings, dict['parser'] is class_name
support_sites = {
    'www.viki.com': {
        'type': 'download',
        'driver_name': 'chrome',
        'parser': 'VikiParser',
    },
    'www.baidu.com': {
        'type': 'stream',
        'driver_name': 'chrome',
        'parser': '',
    },
}




