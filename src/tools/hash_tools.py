#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/10/31 15:26
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : hash_tools.py
# @Software: PyCharm
# @ToUse  :


import hashlib

from src.tools.config_manager import ConfigInit


def hash_md5(content):
    content = str(content)
    content_hash = hashlib.md5()
    content_hash.update(content)
    return content_hash.hexdigest()


def get_hash_sign(file_name):
    return hash_md5(file_name)


if __name__ == '__main__':
    a1 = hash_md5('1542772040')
    a2 = hash_md5('https://content.viki.io/1138126v/dash/1138126v_dash_high_480p_dce91c_1809251045_track2_dashinit.mp4')
    pass
