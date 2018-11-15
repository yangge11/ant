#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/2 11:51
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : save_worker_start.py
# @Software: PyCharm
# @ToUse  :
import logging
import time
from optparse import OptionParser
import sys

sys.path.append('../')

from src.tools import consts, logger
from src.tools.queue_manager import RedisMsgQueue
from src.worker.save_worker import DBSaveWorker


def run():
    task_queue = RedisMsgQueue()
    task_queue.addQueue(consts.constant_manager.DB_SAVE_QUEUE_NAME, 20480)
    db_save_worker = DBSaveWorker(consts.constant_manager.DB_SAVE_QUEUE_NAME, task_queue, 3)
    db_save_worker.start()

    while True:
        logging.info("=================> queue_size: %d", task_queue.size(consts.constant_manager.DB_SAVE_QUEUE_NAME))
        time.sleep(10)


if __name__ == "__main__":
    logger.init_log()
    opt = OptionParser()
    opt.add_option('--redis_ip',
                   dest='redis_ip',
                   type=str,
                   help='the ip of the redis server')
    opt.add_option('--redis_port',
                   dest='redis_port',
                   type=int,
                   help='the port of the check host')
    (options, args) = opt.parse_args()
    run()
