#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.
import thread

import logging

__author__ = 'zengyaopeng@tv365.net(ZengYaoPeng)'


def init_log():
    logging.basicConfig(format="[%(levelname)s %(threadName)s %(asctime)s %(filename)s:%(lineno)d] %(message)s",
                        level=logging.DEBUG)
