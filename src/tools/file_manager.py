#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/14 15:10
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : file_manager.py
# @Software: PyCharm
# @ToUse  :
import logging
import os
import re
import traceback

import paramiko


def get_file_size(file_absolute_path):
    return os.path.getsize(file_absolute_path)


def exist_file(file_absolute_path):
    return os.path.exists(file_absolute_path)


def del_file(file_absolute_path):
    return os.remove(file_absolute_path)


def get_file_name_by_download_url(download_url):
    begin_list = [i.start() for i in re.finditer('/', download_url)]
    if download_url.find('.', begin_list[-1]) != -1:
        file_name = download_url[begin_list[-1] + len('/'):download_url.find('.', begin_list[-1])]
    else:
        file_name = download_url[begin_list[-1] + len('/'):]
    file_name = file_name.replace('.', '').replace(' ', '')
    return file_name


def rename_files(files):
    for download_file in files:
        try:
            os.rename(download_file, download_file[:-4] + '.ant')
        except:
            traceback.print_exc()
            logging.error('error rename file for %s' % download_file)
    pass


if __name__ == '__main__':
    # get_file_name_by_download_url(
    #     'https://www.viki.com/videos/200085v-goodbye-dear-wife-episode-18')
    pass
