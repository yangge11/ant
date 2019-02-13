#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/10/24 14:28
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : queue_worker.py
# @Software: PyCharm
# @ToUse  :
import Queue
import threading
from abc import ABCMeta, abstractmethod

import redis

from src.tools.config_manager import ConfigInit


class MsgQueue(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def init(self, host='', port=''): pass

    @abstractmethod
    def addQueue(self, queue_name, max_size): pass

    @abstractmethod
    def push(self, key, content): pass

    @abstractmethod
    def pop(self, key): pass

    @abstractmethod
    def size(self, key): pass


class LocalMsgQueue(MsgQueue):
    _queue_map = {}
    _queue_max_size = -1
    _lock = threading.Lock()

    def __init__(self):
        pass

    def init(self, host='', port=''):
        pass

    def addQueue(self, queue_name, max_size):
        if queue_name in self._queue_map:
            return False
        self._queue_map[queue_name] = Queue.Queue(max_size)

    def push(self, key, content):
        if key not in self._queue_map:
            return False
        self._queue_map[key].put(content)

    def pop(self, key):
        if key not in self._queue_map:
            return None
        res = self._queue_map[key].get_nowait()
        return res

    def size(self, key):
        if key not in self._queue_map:
            return -1
        res = self._queue_map[key].qsize()
        return res


class RedisMsgQueue(MsgQueue):
    def __init__(self, host=ConfigInit().get_config_by_option('redis_ip'), port=6379):
        self.__db = None
        self.init(host, port)

    def init(self, host, port, decode_responses=True):
        self.__db = redis.Redis(host=host, port=port)

    def addQueue(self, queue_name, max_size):
        return True

    def hash_add(self, name, key, content):
        return self.__db.hset(name, key, content)

    def set_add(self, key, *content):
        return self.__db.sadd(key, *content)

    def set_exist(self, key, content):
        return self.__db.sismember(key, content)

    def set_size(self, key):
        return self.__db.scard(key)

    def set_get_all(self, key):
        return self.__db.smembers(key)

    def s_pop(self, key):
        return self.__db.spop(key)

    def l_push(self, key, content):
        self.__db.lpush(key, content)

    def push(self, key, content):
        self.__db.rpush(key, content)

    def pop(self, key):
        return self.__db.lpop(key)

    def size(self, key):
        return self.__db.llen(key)

    def hash_set(self, queue_name, key, value):
        return self.__db.hset(queue_name, key, value)

    def hash_get(self, queue_name, key):
        return self.__db.hget(queue_name, key)

    def hash_del(self, queue_name, keys_tuple):
        return self.__db.hdel(queue_name, keys_tuple)

    def hash_get_all(self, queue_name):
        return self.__db.hgetall(queue_name)
