#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/2 11:22
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : scheduler.py
# @Software: PyCharm
# @ToUse  :
import logging

import requests

from src.dao.download_media_dao import save
from src.entity.medias import from_json_to_string, DownloadMedia
from src.tools import logger, consts
from src.tools.config_manager import ConfigInit
from src.tools.queue_manager import RedisMsgQueue


def scheduler_controller_queue(url):
    task_queue = RedisMsgQueue()
    task_queue.addQueue(consts.constant_manager.CONTROLLER_QUEUE_NAME, 1)
    task_queue.push(consts.constant_manager.CONTROLLER_QUEUE_NAME, url)
    logging.debug('push task url %s' % url)


def scheduler_db_save_queue(download_media_json):
    # version1==>version2
    # redis_queue = RedisMsgQueue()
    # redis_queue.addQueue(consts.constant_manager.DB_SAVE_QUEUE_NAME, 1)
    # redis_queue.push(consts.constant_manager.DB_SAVE_QUEUE_NAME, from_json_to_string(download_media_json))
    # logging.debug('push db_save download_url %s' % download_media_json['download_url'])
    download_media_id = save(DownloadMedia().from_json_to_obj(download_media_json))
    logging.debug('save download media finish %s' % download_media_id)
    pass


def scheduler_download_status_queue(download_file_status_json):
    redis_queue = RedisMsgQueue()
    redis_queue.addQueue(consts.constant_manager.DOWNLOAD_STATUS_QUEUE_NAME, 1)
    redis_queue.set_add(consts.constant_manager.DOWNLOAD_STATUS_QUEUE_NAME,
                        from_json_to_string(download_file_status_json))
    logging.debug('push download_file_status hash_sign %s' % download_file_status_json['hash_sign'])
    pass


def scheduler_download_queue(download_file_json, priority=False):
    redis_queue = RedisMsgQueue()
    redis_queue.addQueue(consts.constant_manager.DOWNLOAD_QUEUE_NAME, 1)
    if priority:
        redis_queue.l_push(consts.constant_manager.DOWNLOAD_QUEUE_NAME, from_json_to_string(download_file_json))
    else:
        redis_queue.push(consts.constant_manager.DOWNLOAD_QUEUE_NAME, from_json_to_string(download_file_json))
    logging.debug('push download_file download_url %s' % download_file_json['download_url'])
    pass


def scheduler_remote_service(urls):
    remote_ip = ConfigInit().get_config_by_option('remote_ip')
    urls_to_remote = ['http://%s:8080/to_controller?url=%s' % (remote_ip, url) for url in urls]
    for url_to_remote in urls_to_remote:
        response = requests.get(url_to_remote)
        logging.debug(response.text)
    pass


def main():
    scheduler_remote_service()
    pass


if __name__ == '__main__':
    logger.init_log()
    main()
