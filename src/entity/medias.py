#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/1 16:26
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : medias.py
# @Software: PyCharm
# @ToUse  :
import json
import traceback

from src.tools import consts


def from_string_to_json(content):
    try:
        json_dict = json.loads(content)
        json_dict = normalize_dict(json_dict)
    except Exception as e:
        traceback.print_exc()
        pass
    return json_dict


def from_json_to_string(data):
    data = normalize_dict(data)
    return json.dumps(data, ensure_ascii=False)


def normalize_dict(data):
    if type(data) == dict:
        new_data = {}
        for k in data:
            data[k] = normalize_dict(data[k])
            if type(k) == unicode:
                new_data[k.encode('utf-8')] = data[k]
            else:
                new_data[k] = data[k]
        data = new_data
    elif type(data) == list:
        for i in range(0, len(data)):
            data[i] = normalize_dict(data[i])
    elif type(data) == unicode:
        data = data.encode('utf-8')
    else:
        data = str(data)
    return data


class JsonSerializable(object):
    def from_string_to_obj(self, json_str):
        json_obj = from_string_to_json(json_str)
        return self.from_json_to_obj(json_obj)

    def from_obj_to_string(self):
        return json.dumps(vars(self), ensure_ascii=False)

    def from_json_to_obj(self, json_obj):
        for key in vars(self.__class__):
            if key in json_obj:
                setattr(self, key, json_obj[key])
        return self

    def from_obj_to_json(self):
        return from_string_to_json(json.dumps(vars(self), ensure_ascii=False))


class DownloadMedia(JsonSerializable):
    """
    对应数据表download_media
    """
    id = 0
    cloud_path = ''
    video_url = ''
    original_url = ''
    download_url = ''
    total_size = 0
    media_quality = ''
    episode = 0
    download_path = ''
    media_name = ''
    absolute_path = ''
    media_type = ''
    file_type = ''
    upload_status = ''
    hash_sign = ''
    download_status = ''
    create_time = ''
    update_time = ''
    site = ''
    language = ''
    merged_sign = ''
    merged_order = 0
    merged_status = ''

    def __init__(self):
        pass


class DownloadFile(DownloadMedia):
    """
    由下载器管理的核心对象
    """
    download_url = ''
    total_size = ''
    absolute_path = ''
    file_type = ''
    download_status = ''
    merged_sign = ''
    merged_order = 0
    merged_status = ''
    download_path = ''
    site = ''
    file_name = ''
    original_url = ''
    download_type = ''

    def __init__(self, download_url='', total_size='', absolute_path='', file_type='', download_status='',
                 merged_sign='', merged_order=0, merged_status='', download_path='', site='',
                 file_name='', original_url='', download_type=consts.constant_manager.CONTINUE_DOWNLOAD):
        self.download_url = download_url
        self.total_size = total_size
        self.absolute_path = absolute_path
        self.file_type = file_type
        self.download_status = download_status
        self.merged_sign = merged_sign
        self.merged_order = merged_order
        self.merged_status = merged_status
        self.download_path = download_path
        self.site = site
        self.file_name = file_name
        self.original_url = original_url
        self.download_type = download_type


single_stream_file_json = {
    'download_url': '',
    'priority': 0,  # default pirioity is 0
    'media_type': '',  # audio，video，subtitle
    'media_quality': '',  # if audio or video is 480p,360p...
    'language': '',  # subtitles is en,de,ch...
    'merged_sign': '',
    'merged_order': 0,
}

download_file_status = {
    'hash_sign': '',
    'total_size': 0,
    'now_size': 0,
    'download_speed': 0
}


class StreamInfo(DownloadMedia):
    """
    解析器需要的数据:
    original_url；download_url；media_quality；episode；media_name；media_type；language；
    """
    original_url = ''
    episode = ''
    media_name = ''
    site = ''

    def __init__(self, video_url, media_name, download_file_list, site, type, episode, original_url):
        self.video_url = video_url
        self.media_name = media_name
        self.download_file_list = download_file_list
        self.site = site
        self.type = type  # stream or download
        self.episode = episode
        self.original_url = original_url
        pass


class DBConnector(JsonSerializable):
    DBHOST = ''
    DBPORT = 1
    DBUSER = ''
    DBPWD = ''
    DBNAME = ''
    DBCHAR = ''
    DB_FULL_NAME = ''

    def __init__(self):
        pass
