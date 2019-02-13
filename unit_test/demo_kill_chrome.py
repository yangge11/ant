#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/17 17:14
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : demo_kill_chrome.py
# @Software: PyCharm
# @ToUse  :
import logging
import os
import time
import sys

sys.path.append('../')
from src.tools import logger


def kill_chrome_process():
    logging.debug('begin')
    os.system("ps x|grep chrome|grep -v grep |awk '{print $1}'|xargs kill -9")
    pass


if __name__ == '__main__':
    kill_chrome_process()
    logger.init_log()
