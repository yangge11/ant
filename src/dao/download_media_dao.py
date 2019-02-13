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
        download_media.id = insert(download_media)
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
    select * from crawler_online.download_media where merged_order not in (0,-1) and download_status=1 
    and merged_status is null and download_path!='/data/dev_ant/';
    """
    client = ConfigInit().get_conn()
    return client.getAll(sql)


def select_original_url_downloaded_subtitle(urls_list):
    sql = """
    select distinct original_url from download_media
    where 
    media_type='subtitle' and download_status=1
    and original_url in (%s);
    """ % ', '.join(map(lambda x: "'%s'" % x, urls_list))
    client = ConfigInit().get_conn()
    urls_tuple = client.getAll(sql)
    return [url_dict['original_url'] for url_dict in urls_tuple] if urls_tuple else []


def select_original_url_downloaded_video_audio(urls_list):
    sql = """
    select original_url from crawler_online.download_media
    where 
    (media_type='video' or media_type='audio' ) and download_status=1 and original_url in (%s)
    group by original_url having count(original_url)>1;""" % ', '.join(map(lambda x: "'%s'" % x, urls_list))
    client = ConfigInit().get_conn()
    urls_tuple = client.getAll(sql)
    return [url_dict['original_url'] for url_dict in urls_tuple] if urls_tuple else []


def select_original_url_downloaded_merged_media(urls_list):
    sql = """
    select original_url from crawler_online.download_media
    where media_type='merged' and file_type='mp4' and download_status=1 and original_url in (%s)
    ;""" % ', '.join(map(lambda x: "'%s'" % x, urls_list))
    client = ConfigInit().get_conn()
    urls_tuple = client.getAll(sql)
    return [url_dict['original_url'] for url_dict in urls_tuple] if urls_tuple else []


def select_tmp():
    sql = """
    select id,original_url,absolute_path,download_url,media_type,language,file_type 
    from crawler_online.download_media
    """
    client = ConfigInit().get_conn()
    all_tuple = client.getAll(sql)
    return all_tuple


def select_scp_file():
    sql = """
    SELECT absolute_path FROM crawler_online.download_media where download_status=1
    """
    client = ConfigInit().get_conn()
    all_tuple = client.getAll(sql)
    return [url_dict['absolute_path'] for url_dict in all_tuple] if all_tuple else []


def select_not_download_over_file():
    sql = """
    SELECT absolute_path FROM crawler_online.download_media where download_status!=1;
    """
    client = ConfigInit().get_conn()
    all_tuple = client.getAll(sql)
    return [url_dict['absolute_path'] for url_dict in all_tuple] if all_tuple else []


def del_wrong_db_data():
    pass
