#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/1 11:45
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : monitor_worker.py
# @Software: PyCharm
# @ToUse  : 监控器，用于监控内存中需要ffmpeg处理的媒体文件
import json
import logging
import time

from src.dao.download_media_dao import select_to_merge
from src.entity.medias import from_string_to_json, from_json_to_string
from src.tools import consts
from src.tools.queue_manager import RedisMsgQueue
from src.worker.download_worker import MediaProcess
from src.worker.save_worker import DBSaveWorker


def monitor_download_status():
    """
    1.读取内存中的即下载文件，以及总大小
    2.读取这些文件目前大小，以及间隔时间的下载速度(每秒讀取一次)
    :return:
    """
    # todo:性能优化，通用下载器的文件下载监控方式
    redis_queue = RedisMsgQueue()
    while True:
        all_files_old_json = redis_queue.set_get_all(consts.constant_manager.DOWNLOAD_STATUS_QUEUE_NAME)
        for single_file_json in all_files_old_json:
            single_file_json['now_size'] = '读取文件大小'
        time.sleep(3)
        all_files_new_json = redis_queue.set_get_all(consts.constant_manager.DOWNLOAD_STATUS_QUEUE_NAME)
        for single_file_json in all_files_new_json:
            single_file_json['now_size'] = '读取文件大小'
            single_file_json['download_speed'] = ('now_size' - 'now_size') / 3
            # 修改最新值，重新一个个放入内存中
            if 'download_speed' <= 0:
                '塞入队列重新下载'
    pass


def upload_file():
    """
    1.查找下载完成了并且可以上传的video或者字幕文件
    2.根据特定规则，进行上传操作
    3.上传完成后给到存储器进行数据存储
    :return:
    """
    # todo:上传云盘操作
    to_upload_file = '查库'
    '上传'
    '根据回调函数进行数据存储'
    pass


def merge_download_media():
    download_media_dict_tuple = select_to_merge()
    redis_queue = RedisMsgQueue()
    order_dict = {}
    if not download_media_dict_tuple:
        logging.debug('no media to merged')
        return
    for download_media_dict in download_media_dict_tuple:
        if download_media_dict['merged_sign'] not in order_dict.keys():
            order_dict[download_media_dict['merged_sign']] = []
        order_dict[download_media_dict['merged_sign']].append(download_media_dict)
    for merged_sign in order_dict.keys():
        redis_queue.push(consts.constant_manager.FILE_MERGE_QUEUE_NAME, from_json_to_string(order_dict[merged_sign]))
    media_process_worker = MediaProcess(consts.constant_manager.FILE_MERGE_QUEUE_NAME, redis_queue, 10)
    media_process_worker.start()
    media_process_worker.wait()
    pass
