#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/10/23 14:25
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : download_worker.py
# @Software: PyCharm
# @ToUse  :


"""
1.task_queue封装
2.消费者封装
3.单用户自定义下载功能，程序批量下载功能
5.下载状态监控
6.媒体处理和转换功能
7.宽带自定义控制
8.下载队列优先级的处理
"""

# todo:下载队列优先级的控制处理
import copy
import gzip
import json
import logging
import random
import traceback
import urllib2
from Queue import Empty
from contextlib import closing
from threading import currentThread

import os
import requests
import threadpool
import time

from ffmpy import FFmpeg

from app.scheduler import scheduler_db_save_queue, scheduler_download_status_queue
from src.dao.download_media_dao import select_by_hash_sign
from src.entity.medias import from_string_to_json, DownloadFile, from_json_to_string, download_file_status
from src.tools import consts
from src.tools.file_manager import get_file_size, exist_file, del_file
from src.tools.hash_tools import hash_md5, get_hash_sign
from src.tools.config_manager import ConfigInit
from src.tools.queue_manager import RedisMsgQueue
from src.worker.stream_worker import get_and_download_stream_obj
from src.worker.worker import Worker


def get_file_download_status(file_name):
    """
    未完成，已完成，下载中
    :param hash_sign:
    :return:
    """
    hash_sign = get_hash_sign(file_name)
    download_status = consts.constant_manager.NOT_DOWNLOAD_OVER
    if has_download_over(hash_sign):
        download_status = consts.constant_manager.DOWNLOAD_OVER
    # elif being_download(hash_sign):
    #     download_status = consts.constant_manager.DOWNLOADING
    return download_status


def has_download_over(hash_sign):
    # todo:兼容其他是否下載的驗證方式
    return True if select_by_hash_sign(hash_sign) else False


def being_download(hash_sign):
    # todo:兼容其他是否下載的驗證方式
    redis_queue = RedisMsgQueue()
    all_files_json = redis_queue.set_get_all(consts.constant_manager.DOWNLOAD_STATUS_QUEUE_NAME)
    for file_str in all_files_json:
        file_json = from_string_to_json(file_str)
        if hash_sign == file_json['hash_sign']:
            return True
    return False


class Downloader(Worker):
    def process(self, content):
        download_file_obj = DownloadFile().from_string_to_obj(content)
        if get_file_download_status(download_file_obj.file_name) != consts.constant_manager.NOT_DOWNLOAD_OVER:
            logging.debug('file is downloading or download over %s' % download_file_obj.download_url)
        else:
            logging.debug('file to be download is %s' % download_file_obj.download_url)
            self.download_media(download_file_obj)

    def pause(self):
        # todo:下载暂停
        pass

    def modify_queue(self):
        # todo:下载队列调控
        pass

    def pre_parse_download_obj(self, download_file_obj):
        # type: (DownloadFile) -> None
        """
        :param download_file_obj:
        :return:
        """
        headers = {'User-Agent': random.choice(consts.constant_manager.USER_AGENTS)}
        response = requests.get(download_file_obj.download_url, stream=True, headers=headers)
        headers_json = dict(response.headers)
        if 'mp4' in headers_json['Content-Type']:
            download_file_obj.file_type = 'mp4'
        elif 'text' in headers_json['Content-Type']:
            download_file_obj.file_type = 'txt'
        else:
            logging.error('unknow file_type in %s' % download_file_obj.download_url)
        try:
            download_file_obj.total_size = int(headers_json['Content-Length'])
        except:
            logging.error('can not get total_size from download_url %s' % download_file_obj.download_url)
        if download_file_obj.file_name == '':
            download_file_obj.file_name = hash_md5(download_file_obj.download_url)
        download_file_obj.hash_sign = get_hash_sign(file_name=download_file_obj.file_name)
        if download_file_obj.download_path == '':
            download_file_obj.download_path = ConfigInit().get_download_path()
        # todo:gzip压缩文件的续下载问题
        if 'Content-Encoding' in headers_json and headers_json['Content-Encoding'] == 'gzip':
            download_file_obj.download_type = 'wb+'
        download_file_obj.absolute_path = download_file_obj.download_path + download_file_obj.file_name + '.' + download_file_obj.file_type

    def download_media(self, download_file_obj):
        # type: (DownloadFile) -> None
        """
        同样下载文件的定义：如果是一样路径一样名称，一样大小，则认为同样文件
        有没有下载同样的链接，存储在对方端上本地
        只负责下载和续下载，不做其他逻辑处理
        todo:多线程下载同一队列大文件支持,自动创建默认下载路径,字幕下载的文件URl是不同的（暂时无法续下载）
        :param download_file_obj:name,file_type,file_path均可以给出默认值，original_url
        :return:
        """
        new_download_file_obj = download_file_obj
        self.pre_parse_download_obj(download_file_obj)

        download_media_json = {
            'hash_sign': download_file_obj.hash_sign,
            'total_size': download_file_obj.total_size,
            'download_url': download_file_obj.download_url,
            'absolute_path': download_file_obj.absolute_path,
            'file_type': download_file_obj.file_type,
            'download_status': consts.constant_manager.NOT_DOWNLOAD_OVER,
        }

        if exist_file(download_file_obj.absolute_path) and get_file_size(
                download_file_obj.absolute_path) == download_file_obj.total_size:
            logging.debug('same file %s' % download_file_obj.absolute_path)
            download_media_json['download_status'] = consts.constant_manager.DOWNLOAD_OVER
            if ConfigInit().get_config_by_option('save_db'):
                scheduler_db_save_queue(download_media_json)
            return
        elif os.path.exists(download_file_obj.absolute_path):
            temp_size = os.path.getsize(download_file_obj.absolute_path)
        else:
            temp_size = 0
        headers = {'User-Agent': random.choice(consts.constant_manager.USER_AGENTS)}
        headers.update({'Range': 'bytes=%d-' % temp_size})

        with closing(requests.get(download_file_obj.download_url, stream=True,
                                  headers=headers)) as response:
            chunk_size = 1024
            progress = ProgressBar(download_file_obj.absolute_path, total=download_file_obj.total_size, unit="KB",
                                   chunk_size=chunk_size,
                                   run_status="正在下载", fin_status="下载完成")

            with open(download_file_obj.absolute_path, download_file_obj.download_type) as file:
                # todo:通用下载器，调整此处逻辑
                download_file_status_json = copy.deepcopy(download_file_status)
                download_file_status_json['hash_sign'] = download_file_obj.hash_sign
                download_file_status_json['total_size'] = download_file_obj.total_size
                logging.debug('start download file %s' % download_file_obj.download_url)
                scheduler_download_status_queue(download_file_status_json)
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    progress.refresh(count=len(data))
                    # todo:if发现优先级高的下载队列，self.pause()

        download_media_json['download_status'] = 1
        if ConfigInit().get_config_by_option('save_db'):
            scheduler_db_save_queue(download_media_json)


class MediaProcess(Worker):
    def process(self, content):
        to_merged_medias_lists = from_string_to_json(content)
        merged_absolue_path = self.merge_media(to_merged_medias_lists)
        # todo：原子性操作此次批量数据库操作
        if merged_absolue_path:
            download_media_json = copy.deepcopy(to_merged_medias_lists[0])
            del download_media_json['id']
            download_media_json['absolute_path'] = merged_absolue_path
            download_media_json['media_type'] = consts.constant_manager.MERGED
            download_media_json['total_size'] = get_file_size(merged_absolue_path)
            download_media_json['hash_sign'] = get_hash_sign(download_media_json['merged_sign'])
            download_media_json['download_status'] = ''
            download_media_json['merged_order'] = ''
            scheduler_db_save_queue(download_media_json)
            for download_media_json in to_merged_medias_lists:
                download_media_json['merged_status'] = '1'
                scheduler_db_save_queue(download_media_json)
            pass

    def merge_media(self, to_merged_medias_lists):
        # to_merged_medias_dict：[download_media_obj1,download_media_obj2,......]
        inputs = {}
        merged_absolue_path = ''.join(
            [ConfigInit().get_download_path(), hash_md5(to_merged_medias_lists[0]['merged_sign']), '.mp4']
        )
        outputs = {merged_absolue_path: '-c copy'}
        # todo:强制ffmpeg合并处理
        if exist_file(merged_absolue_path):
            del_file(merged_absolue_path)
        for to_merged_media_dict in to_merged_medias_lists:
            inputs[to_merged_media_dict['absolute_path']] = ''
        ff = FFmpeg(inputs=inputs, outputs=outputs)
        ff.run()
        return merged_absolue_path


class ProgressBar(object):
    # todo:整合在监控器里面
    def __init__(self, title, count=0.0, run_status=None, fin_status=None, total=100.0, unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "[%s] %s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.statue)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (
            self.title, self.status, self.count / self.chunk_size, self.unit, self.seq, self.total / self.chunk_size,
            self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        logging.debug(self.__get_info() + end_str)
