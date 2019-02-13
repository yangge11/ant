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
import sys
import time
from optparse import OptionParser

sys.path.append('../../')
from src.tools.file_manager import rename_files, get_file_size

from app.scheduler import scheduler_remote_service, scheduler_controller_queue, scheduler_download_status_queue
from src.dao.download_media_dao import select_to_merge, select_original_url_downloaded_subtitle, \
    select_original_url_downloaded_video_audio, select_original_url_downloaded_merged_media, \
    select_not_download_over_file
from src.entity.medias import from_string_to_json, from_json_to_string
from src.tools import consts, logger
from src.tools.queue_manager import RedisMsgQueue
from src.worker.download_worker import MediaProcess
from src.worker.save_worker import DBSaveWorker
from unit_test.crawl_viki_demo import get_paly_urls, write_urls


def monitor_download_status():
    redis_queue = RedisMsgQueue()
    while True:
        all_files_old_json = redis_queue.hash_get_all(consts.constant_manager.DOWNLOAD_STATUS_QUEUE_NAME)
        for hash_sign in all_files_old_json.keys():
            all_files_old_json[hash_sign] = from_string_to_json(all_files_old_json[hash_sign])
            all_files_old_json[hash_sign]['now_size'] = get_file_size(all_files_old_json[hash_sign]['absolute_path'])
        time.sleep(10)  # 5分钟下载中文件大小不变化，认为下载服务异常挂掉，删除下载队列
        all_files_new_json = redis_queue.hash_get_all(consts.constant_manager.DOWNLOAD_STATUS_QUEUE_NAME)
        for hash_sign in all_files_new_json:
            all_files_new_json[hash_sign] = from_string_to_json(all_files_new_json[hash_sign])
            all_files_new_json[hash_sign]['now_size'] = get_file_size(all_files_new_json[hash_sign]['absolute_path'])
            if int(all_files_new_json[hash_sign]['now_size']) - int(all_files_old_json[hash_sign]['now_size']) == 0:
                redis_queue.hash_del(consts.constant_manager.DOWNLOAD_STATUS_QUEUE_NAME, hash_sign)
        logging.debug('monitor download queue')
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
    logging.debug('merge_download_media begin')
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
        if len(order_dict[merged_sign]) == 2:
            redis_queue.push(consts.constant_manager.FILE_MERGE_QUEUE_NAME,
                             from_json_to_string(order_dict[merged_sign]))
    media_process_worker = MediaProcess(consts.constant_manager.FILE_MERGE_QUEUE_NAME, redis_queue, 10)
    media_process_worker.start()
    media_process_worker.wait()


def scheduler_failed_play_url():
    # run per hour
    logging.debug('scheduler_failed_play_url begin')
    redis_queue = RedisMsgQueue()
    if redis_queue.size('demo') <= 0 and redis_queue.size('download_queue') <= 0 \
            and redis_queue.size('controller_queue') <= 0:
        logging.debug('start re_crawl urls')
        urls = get_paly_urls()
        write_urls(urls)
        urls = [url.replace('\n', '') for url in open('/data/my_ant/play_urls').readlines()]
        urls_downloaded_subtitle = select_original_url_downloaded_subtitle(urls)
        urls_downloaded_media = select_original_url_downloaded_video_audio(urls)
        urls_downloaded_merged_media = select_original_url_downloaded_merged_media(urls)
        urls_to_parse_subtitle = set(urls) - set(urls_downloaded_subtitle)
        urls_to_parse_media = set(urls) - set(urls_downloaded_media) - set(urls_downloaded_merged_media)
        urls_to_parse = urls_to_parse_subtitle | urls_to_parse_media
        # scheduler_remote_service(urls_to_parse)
        for url in urls_to_parse:
            scheduler_controller_queue(url)


def rename_not_download_over_file():
    not_download_over_files = select_not_download_over_file()
    rename_files(not_download_over_files)
    pass


def del_wrong_db_data():
    # todo:check wrong db_data
    pass


def demo_opt():
    logging.debug('demo begin')
    pass


if __name__ == '__main__':
    logger.init_log()
    opt = OptionParser()
    opt.add_option('--func_name',
                   type=str,
                   dest='func_name',
                   help='the func_name of the monitor_worker')
    (options, args) = opt.parse_args()
    func_name = options.func_name
    # func_name = 'merge_download_media'
    if func_name in locals().keys():  # safe set
        eval(func_name)()
