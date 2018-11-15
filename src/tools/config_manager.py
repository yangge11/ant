#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/10/24 17:01
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : config_manager.py
# @Software: PyCharm
# @ToUse  :


import ConfigParser

import os
import sys

from src.dao.mysql_pool import MysqlPoolClient
from src.entity.medias import DBConnector


class ConfigInit(object):
    __instance = None
    _conf = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self._conf = self.get_conf()
        pass

    def get_conf(self):
        if not self._conf:
            self._conf = ConfigParser.ConfigParser()
            project_real_path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../"))
            self._conf.read(project_real_path + '/src/config/deploy.ini')
            self._conf.set('DEFAULT', 'deploy_home', project_real_path)
            # sys.path.append(project_real_path)
        return self._conf

    def get_conn(self, table_name='download_media'):
        if table_name == 'download_media':
            section_download_media_name = self.get_config_by_option('db_download_media')
            db_conf = {
                'DB_FULL_NAME': self._conf.get(section_download_media_name, 'DB_FULL_NAME'),
                'DBHOST': self._conf.get(section_download_media_name, 'DBHOST'),
                'DBPORT': self._conf.get(section_download_media_name, 'DBPORT'),
                'DBUSER': self._conf.get(section_download_media_name, 'DBUSER'),
                'DBPWD': self._conf.get(section_download_media_name, 'DBPWD'),
                'DBNAME': self._conf.get(section_download_media_name, 'DBNAME'),
                'DBCHAR': self._conf.get(section_download_media_name, 'DBCHAR'),
            }
        conn = MysqlPoolClient(DBConnector().from_json_to_obj(db_conf))
        return conn

    def get_config_by_option(self, option_name):
        section_config_name = self._conf.get('DEFAULT', 'config')
        return self.get_conf().get(section_config_name, option_name)

    def get_project_path(self):
        return self.get_conf().get('DEFAULT', 'deploy_home')

    def get_download_path(self):
        return self.get_config_by_option('download_path')
