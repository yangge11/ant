#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/2 10:49
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : controller_worker_start.py
# @Software: PyCharm
# @ToUse  :
import logging
from optparse import OptionParser
import time
import sys
sys.path.append('../')
from src.tools import logger, consts
from src.tools.queue_manager import RedisMsgQueue
from src.worker.controler_worker import Controller


def run():
    task_queue = RedisMsgQueue()
    task_queue.addQueue(consts.constant_manager.CONTROLLER_QUEUE_NAME, 20480)
    controller_worker = Controller(consts.constant_manager.CONTROLLER_QUEUE_NAME, task_queue, 10)
    controller_worker.start()

    while True:
        logging.info("=================> queue_size: %d", task_queue.size(consts.constant_manager.CONTROLLER_QUEUE_NAME))
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
