#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/10/25 21:24
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : controler_worker.py
# @Software: PyCharm
# @ToUse  :

# 管理器：负责各方面的连接，url-->管理器-->解析器-->管理器-->下载器-->管理器-->存储器
import random
import requests

from app.scheduler import scheduler_download_queue, scheduler_db_save_queue
from src.entity.medias import from_string_to_json, DownloadFile, from_json_to_string, DownloadMedia
from src.tools import consts, logger
from src.tools.hash_tools import hash_md5, get_hash_sign
from src.tools.config_manager import ConfigInit
from src.tools.queue_manager import LocalMsgQueue, RedisMsgQueue
from src.worker.stream_worker import get_and_download_stream_obj
from src.worker.worker import Worker


class Controller(Worker):

    def process(self, content):
        response_stream = from_string_to_json(get_and_download_stream_obj(content))

        if response_stream['type'] == consts.constant_manager.DOWNLOAD:
            for download_info in response_stream['download_file_list']:
                file_name = hash_md5(download_info['download_url'])
                if download_info['media_type'] == consts.constant_manager.SUBTITLE:
                    file_name = response_stream['site'] + '_' + hash_md5(response_stream['original_url']) + \
                                '_' + download_info['language']
                file_obj = DownloadFile(download_url=download_info['download_url'], file_name=file_name,
                                        site=response_stream['site'], original_url=response_stream['original_url'])

                download_media_json = {
                    'video_url': response_stream['video_url'],
                    'original_url': response_stream['original_url'],
                    'download_url': download_info['download_url'],
                    'media_quality': download_info['media_quality'],
                    'episode': response_stream['episode'],
                    'download_path': ConfigInit().get_config_by_option('download_path'),
                    'media_name': response_stream['media_name'],
                    'hash_sign': get_hash_sign(file_name),
                    'media_type': download_info['media_type'],
                    'site': response_stream['site'],
                    'language': download_info['language'],
                    'merged_sign': download_info['merged_sign'],
                    'merged_order': download_info['merged_order'],
                }
                scheduler_db_save_queue(download_media_json)

                # todo:下载优先级细粒度管理
                if int(download_info['priority']) > 50:
                    scheduler_download_queue(file_obj.from_obj_to_json(), priority=True)
                else:
                    scheduler_download_queue(file_obj.from_obj_to_json())
        return response_stream
