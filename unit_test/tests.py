#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/10/23 19:32
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : tests.py
# @Software: PyCharm
# @ToUse  :
import traceback
import unittest

from src.worker.stream_worker import VikiParser, get_and_download_stream_info


class Stream_Worker_Test(unittest.TestCase):
    def __init__(self):
        pass

    def setUp(self):
        self.vikiparser = VikiParser()

    def tearDown(self):
        self.vikiparser = None

    def test_viki_parser(self):
        # 1000次结果测试
        self.assertEqual(self.vikiparser.parser('www.baidu.com'), '')
        pass

    def test_get_and_download_stream_info(self):
        self.assertEquals(
            get_and_download_stream_info('https://www.viki.com/videos/1138126v-all-out-of-love-episode-3'), '')
        pass


def main():
    try:
        suite = unittest.TestSuite()
        # suite.addTest(Stream_Worker_Test.test_viki_parser())
        # suite.addTest(Stream_Worker_Test('test_get_and_download_stream_info'))
        runner = unittest.TextTestRunner()
        runner.run(suite)
    except:
        traceback.print_exc()
    pass


if __name__ == '__main__':
    main()
