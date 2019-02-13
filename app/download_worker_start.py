#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/2 11:34
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : download_worker_start.py
# @Software: PyCharm
# @ToUse  :
import logging
import time
from optparse import OptionParser
import sys

sys.path.append('../')
from src.tools import consts, logger
from src.tools.queue_manager import RedisMsgQueue
from src.worker.download_worker import Downloader


def run(queue_name):
    task_queue = RedisMsgQueue()
    task_queue.addQueue(queue_name, 20480)
    downloader_worker = Downloader(queue_name, task_queue, 10)
    downloader_worker.start()

    while True:
        logging.info("queue_name %s==========> queue_size: %d" % (queue_name, task_queue.size(queue_name)))
        time.sleep(10)


if __name__ == "__main__":
    logger.init_log()
    opt = OptionParser()
    opt.add_option('--queue_name',
                   dest='queue_name',
                   type=str,
                   help='the queue_name')
    (options, args) = opt.parse_args()
    run(options.queue_name)
