#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/5 15:07
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : download_media_dao.py
# @Software: PyCharm
# @ToUse  :


import logging
import threading

from src.dao.sql_helper import build_update_sql, build_insert_sql
from src.entity.medias import DownloadMedia
from src.tools import consts
from src.tools.config_manager import ConfigInit


def save(download_media):
    # type: (DownloadMedia) -> long
    logging.debug('save download_media: %s', download_media.download_url)
    sql_client = ConfigInit().get_conn()
    sql_check = 'select id from download_media where hash_sign="%s"' % download_media.hash_sign
    result = sql_client.getOne(sql_check)
    if result:
        download_media.id = result['id']
        update(download_media)
    else:
        insert(download_media)
    return download_media.id


def insert(download_media):
    # type: (DownloadMedia) -> long
    sql = build_insert_sql('download_media', download_media.from_obj_to_json())
    client = ConfigInit().get_conn()
    download_media_id = client.insertOne(sql)
    logging.info("insert new download_media %d, %s" % (download_media_id, download_media.download_url))
    return download_media_id


def update(download_media):
    # type: (DownloadMedia) -> long
    condition_dict = {"id": download_media.id}
    sql = build_update_sql('download_media', download_media.from_obj_to_json(), condition_dict)
    client = ConfigInit().get_conn()
    logging.info('update download_media: %d' % download_media.id)
    return client.update(sql)


def select_by_hash_sign(hash_sign):
    # type: (str) -> long
    sql = 'select id from download_media where hash_sign="%s" and download_status=1' % hash_sign
    client = ConfigInit().get_conn()
    return client.getOne(sql)


def select_to_merge():
    sql = """
    select * from download_media where merged_sign in 
    (select merged_sign from crawler_online.download_media where merged_status!=1 and merged_sign!='' and media_type!="%s"
    group by merged_sign having count(merged_sign)>1)
    order by merged_sign ,merged_order;
    """ % consts.constant_manager.MERGED
    client = ConfigInit().get_conn()
    return client.getAll(sql)
