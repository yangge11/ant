#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/10/24 17:58
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : save_worker_start.py
# @Software: PyCharm
# @ToUse  :
# 拿到对象信息之后，进行相应的数据存储工作,主要存储每一个对象的相关具体信息，进入数据库方便统一管理
from src.dao.download_media_dao import save
from src.entity.medias import DownloadMedia
from src.worker.worker import Worker


class DBSaveWorker(Worker):
    def process(self, download_media_str):
        try:
            download_media_obj = DownloadMedia().from_string_to_obj(download_media_str)
            download_media_id = save(download_media_obj)
        except:
            pass
        pass
