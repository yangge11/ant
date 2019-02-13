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
from src.entity.medias import from_string_to_json, DownloadFile, from_json_to_string, tmp_download_file_status_json
from src.tools import consts
from src.tools.file_manager import get_file_size, exist_file, del_file, get_file_name_by_download_url
from src.tools.hash_tools import hash_md5, get_hash_sign
from src.tools.config_manager import ConfigInit
from src.tools.queue_manager import RedisMsgQueue
from src.worker.worker import Worker


def get_file_download_status(file_name):
    """
    未完成，已完成，下载中
    :param hash_sign:
    :return:
    """
    hash_sign = get_hash_sign(file_name)
    download_status = consts.constant_manager.NOT_DOWNLOAD_OVER
    if select_by_hash_sign(hash_sign):
        download_status = consts.constant_manager.DOWNLOAD_OVER
    elif downloading(file_name):
        download_status = consts.constant_manager.DOWNLOADING
    return download_status


def downloading(file_name):
    # todo:兼容其他是否下載的驗證方式
    redis_queue = RedisMsgQueue()
    if get_hash_sign(file_name) in redis_queue.hash_get_all(consts.constant_manager.DOWNLOAD_STATUS_QUEUE_NAME).keys():
        return True
    return False


class Downloader(Worker):
    def process(self, content):
        try:
            download_file_obj = DownloadFile().from_string_to_obj(content)
            download_status = get_file_download_status(download_file_obj.file_name)
            if download_status in (consts.constant_manager.DOWNLOAD_OVER, consts.constant_manager.DOWNLOADING):
                logging.debug('file is downloading or download over %s' % download_file_obj.download_url)
            else:
                logging.debug('file to be download is %s' % download_file_obj.download_url)
                self.download_media(download_file_obj)
        except:
            traceback.print_exc()
            logging.error('error ===>content %s' % content)

    def pause(self):
        # todo:下载暂停
        pass

    def modify_queue(self):
        # todo:下载队列调控
        pass

    def download_over(self, download_file_obj):
        if exist_file(download_file_obj.absolute_path) and get_file_size(
                download_file_obj.absolute_path) >= download_file_obj.total_size:
            logging.debug('same file has download_over %s' % download_file_obj.absolute_path)
            return True
        return False

    def pre_parse_download_obj(self, download_file_obj):
        # type: (DownloadFile) -> None
        """
        :param download_file_obj:
        :return:
        """
        try:
            headers = {'User-Agent': random.choice(consts.constant_manager.USER_AGENTS)}
            response = requests.get(download_file_obj.download_url, stream=True, headers=headers)
            if response.status_code == 400:
                logging.error('invalid timestamp %s' % download_file_obj.download_url)
                return False
            headers_json = dict(response.headers)
            if 'mp4' in headers_json['Content-Type']:
                download_file_obj.file_type = 'mp4'
            elif 'text' in headers_json['Content-Type']:
                download_file_obj.file_type = 'txt'
            else:
                logging.error('unknow file_type in %s' % download_file_obj.download_url)
                return False
            download_file_obj.total_size = int(headers_json['Content-Length'])
        except:
            traceback.print_exc()
            logging.error('pre_parse_download_obj error download_url %s' % download_file_obj.download_url)
        if download_file_obj.file_name == '':
            download_file_obj.file_name = get_file_name_by_download_url(download_file_obj.download_url)
        download_file_obj.hash_sign = get_hash_sign(file_name=download_file_obj.file_name)
        if download_file_obj.download_path == '':
            download_file_obj.download_path = ConfigInit().get_download_path()
        # todo:gzip压缩文件的续下载问题
        if 'Content-Encoding' in headers_json and headers_json['Content-Encoding'] == 'gzip':
            download_file_obj.download_type = consts.constant_manager.RE_DOWNLOAD
        download_file_obj.absolute_path = download_file_obj.download_path + download_file_obj.file_name + '.' + download_file_obj.file_type
        return True

    def download_media(self, download_file_obj):
        # type: (DownloadFile) -> None
        """
        同样下载文件的定义：如果是一样路径一样名称，一样大小，则认为同样文件
        有没有下载同样的链接，存储在对方端上本地
        只负责下载和续下载，不做其他逻辑处理
        :param download_file_obj:name,file_type,file_path均可以给出默认值，original_url
        :return:
        """
        if not self.pre_parse_download_obj(download_file_obj):
            logging.error('no need to download url %s' % download_file_obj.download_url)
            return

        download_media_json = {
            'hash_sign': download_file_obj.hash_sign,
            'total_size': download_file_obj.total_size,
            'download_url': download_file_obj.download_url,
            'absolute_path': download_file_obj.absolute_path,
            'file_type': download_file_obj.file_type,
            'download_status': consts.constant_manager.NOT_DOWNLOAD_OVER,
        }

        if self.download_over(download_file_obj):
            download_media_json['download_status'] = consts.constant_manager.DOWNLOAD_OVER
            if ConfigInit().get_config_by_option('save_db'):
                logging.debug('save media download_url %s, hash_sign %s' % (
                    download_file_obj.download_url, download_file_obj.hash_sign))
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
            with open(download_file_obj.absolute_path, download_file_obj.download_type) as file:
                chunk_size = 1024
                progress = ProgressBar(download_file_obj.hash_sign, download_file_obj.absolute_path,
                                       total=download_file_obj.total_size, now_size=float(temp_size),
                                       last_size=float(temp_size), unit="KB", chunk_size=chunk_size,
                                       status=consts.constant_manager.DOWNLOADING)
                scheduler_db_save_queue(download_media_json)
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    # if '需要暂停':
                    #     self.pause()
                    progress.refresh(count=len(data))

            progress.refresh(status=consts.constant_manager.DOWNLOAD_OVER)  # 下载队列完成下载

            if self.download_over(download_file_obj):
                download_media_json['download_status'] = consts.constant_manager.DOWNLOAD_OVER
                if ConfigInit().get_config_by_option('save_db'):
                    logging.debug('download over download_url %s, hash_sign %s' % (
                        download_file_obj.download_url, download_file_obj.hash_sign))
                    scheduler_db_save_queue(download_media_json)
            else:
                logging.debug('not download over download_url %s, hash_sign %s' % (
                    download_file_obj.download_url, download_file_obj.hash_sign))


class MediaProcess(Worker):
    def process(self, content):
        to_merged_medias_lists = from_string_to_json(content)
        merged_absolue_path = self.merge_media(to_merged_medias_lists)
        # todo：原子性操作此次批量数据库操作
        if merged_absolue_path:
            download_media_merged_json = copy.deepcopy(to_merged_medias_lists[0])
            del_list = ['id', 'cloud_path', 'create_time', 'merged_status', 'update_time', 'upload_status']
            for del_column in del_list:
                del download_media_merged_json[del_column]
            download_media_merged_json['absolute_path'] = merged_absolue_path
            download_media_merged_json['media_type'] = consts.constant_manager.MERGED
            download_media_merged_json['total_size'] = get_file_size(merged_absolue_path)
            download_media_merged_json['hash_sign'] = get_hash_sign(download_media_merged_json['merged_sign'])
            download_media_merged_json['merged_order'] = -1
            scheduler_db_save_queue(download_media_merged_json)
            for download_media_json in to_merged_medias_lists:
                if exist_file(download_media_json['absolute_path']):
                    del_file(download_media_json['absolute_path'])
                download_media_json['merged_status'] = '1'
                for column in download_media_json.keys():
                    if download_media_json[column] == 'None':
                        del download_media_json[column]
                scheduler_db_save_queue(download_media_json)
            pass

    def merge_media(self, to_merged_medias_lists):
        # to_merged_medias_dict：[download_media_obj1,download_media_obj2,......]
        inputs = {}
        # merged文件名称：merged_sign+'_merged'
        merged_absolue_path = to_merged_medias_lists[0]['absolute_path'][:-len('.mp4')] + '_merged' + '.mp4'
        outputs = {merged_absolue_path: '-c copy'}
        # todo:强制ffmpeg合并处理
        if exist_file(merged_absolue_path):
            logging.debug('%s has exist' % merged_absolue_path)
            return False
            # del_file(merged_absolue_path)
        for to_merged_media_dict in to_merged_medias_lists:
            inputs[to_merged_media_dict['absolute_path']] = ''
        ff = FFmpeg(inputs=inputs, outputs=outputs)
        ff.run()
        return merged_absolue_path


class ProgressBar(object):
    def __init__(self, hash_sign, title, now_size=0.0, status=consts.constant_manager.DOWNLOADING, total=100.0, unit='',
                 sep='/', chunk_size=1.0, speed=0, last_time=time.time(), last_size=0.0):
        super(ProgressBar, self).__init__()
        self.info = "[%s] %s %.2f %s %s %.2f %s"
        self.hash_sign = hash_sign
        self.title = title
        self.total = total
        self.now_size = now_size
        self.chunk_size = chunk_size
        self.status = status
        self.unit = unit
        self.seq = sep
        self.speed = speed
        self.last_time = last_time
        self.last_size = last_size
        self.refresh_count = 0

    def refresh(self, count=0, status=None):
        try:
            self.now_size += count
            self.refresh_count += 1
            now_time = time.time()
            if status is not None:
                self.status = status
                self.downloading_status_manager()
            elif self.refresh_count % consts.constant_manager.DOWNLOAD_SPEED_REFRESH_COUNT == 0:
                self.speed = (self.now_size - self.last_size) / ((now_time - self.last_time) * 1024)  # kb/s
                self.last_size = self.now_size
                self.last_time = now_time
                self.downloading_status_manager()
        except:
            traceback.print_exc()
            pass

    def downloading_status_manager(self):
        if self.status == consts.constant_manager.DOWNLOADING:
            download_file_status_json = copy.deepcopy(tmp_download_file_status_json)
            download_file_status_json['hash_sign'] = self.hash_sign
            download_file_status_json['absolute_path'] = self.title
            download_file_status_json['total_size'] = self.total
            download_file_status_json['now_size'] = self.now_size
            download_file_status_json['download_speed'] = self.speed
            download_file_status_json['status'] = self.status
            scheduler_download_status_queue(download_file_status_json)
        elif self.status == consts.constant_manager.DOWNLOAD_OVER:
            redis_queue = RedisMsgQueue()
            redis_queue.hash_del(consts.constant_manager.DOWNLOAD_STATUS_QUEUE_NAME, self.hash_sign)
