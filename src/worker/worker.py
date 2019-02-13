#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/2 10:33
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : worker.py
# @Software: PyCharm
# @ToUse  : 父类
import logging
import traceback
from Queue import Empty
from threading import currentThread

import time

import threadpool


class Worker(object):
    _task_queue = None
    _input_queue_name = None
    _thread_num = None
    _thread_pool = None
    _stop = False

    def run(self, thread_name):
        currentThread().setName(thread_name)
        logging.debug("thread start")
        download_obj_str = ''
        while True:
            qsize = self._task_queue.size(self._input_queue_name)
            if qsize <= 0 and self._stop:
                break
            try:
                download_obj_str = self._task_queue.pop(self._input_queue_name)
                logging.info("=====> now process %s queue_sise: %d", download_obj_str, qsize)
                if download_obj_str:
                    self.process(download_obj_str)
                else:
                    time.sleep(1)
            except Empty as e:
                logging.info('no task in queue: %s, stop(%s), sleep 10s', self._input_queue_name, str(self._stop))
                time.sleep(10)
            except:
                traceback.print_exc()
                logging.error('error to check in  %s' % download_obj_str)
                time.sleep(5)
            logging.info(str("run %s %s %s" % (
                thread_name, self._task_queue.size(self._input_queue_name), download_obj_str)))
        logging.info("thread finish")

    def __init__(self, input_queue_name, task_queue, thread_num=10):
        self._task_queue = task_queue
        self._input_queue_name = input_queue_name
        self._thread_num = thread_num

    def start(self):
        self._thread_pool = threadpool.ThreadPool(self._thread_num)
        args = []
        for i in range(0, self._thread_num):
            args.append(str("worker_%s_%d" % (self._input_queue_name, i)))
        request_list = threadpool.makeRequests(self.run, args)
        for request in request_list:
            self._thread_pool.putRequest(request)
        self._thread_pool.poll()

    def wait(self):
        logging.info("now start stop current thread...")
        self._stop = True
        self._thread_pool.wait()
        self._thread_pool.dismissWorkers(self._thread_num)
        if self._thread_pool.dismissedWorkers:
            logging.info("Joining all dismissed download_worker threads...%d", len(self._thread_pool.dismissedWorkers))
            self._thread_pool.joinAllDismissedWorkers()

    def process(self, content):
        pass
