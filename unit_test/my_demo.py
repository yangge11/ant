#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/10/25 15:13
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : my_demo.py
# @Software: PyCharm
# @ToUse  :
import ConfigParser
import random
import traceback
from selenium.common.exceptions import TimeoutException
from src.tools.file_manager import del_file
from src.worker.monitor_worker import merge_download_media

from selenium import webdriver

from app.scheduler import scheduler_controller_queue
from src.tools.config_manager import ConfigInit
from src.worker.download_worker import being_download, Downloader

from selenium.webdriver import ChromeOptions, DesiredCapabilities
from src.tools import consts, logger
from src.tools.queue_manager import RedisMsgQueue
from src.worker.controler_worker import Controller


def demo_config():
    conf = ConfigParser.ConfigParser()
    conf.read('/Users/tv365/code/ant/src/config/deploy.ini')
    pass


def demo_controller(urls):
    for url in urls:
        scheduler_controller_queue(url)
        task_queue = RedisMsgQueue()
        controller_worker = Controller(consts.constant_manager.CONTROLLER_QUEUE_NAME, task_queue, 3)
        controller_worker.start()
        controller_worker.wait()
        task_queue.addQueue(consts.constant_manager.DOWNLOAD_QUEUE_NAME, 20480)
        downloader_worker = Downloader(consts.constant_manager.DOWNLOAD_QUEUE_NAME, task_queue, 3)
        downloader_worker.start()
        downloader_worker.wait()
        # task_queue.addQueue(consts.constant_manager.DB_SAVE_QUEUE_NAME, 20480)
        # db_save_worker = DBSaveWorker(consts.constant_manager.DB_SAVE_QUEUE_NAME, task_queue, 3)
        # db_save_worker.start()
        # db_save_worker.wait()
    pass


def demo_merge_file():
    merge_download_media()
    pass


def demo_being_download():
    being_download('edd54d1a7f70873d6b4192b6aca8b5de')
    pass


def demo_mysql():
    conn = ConfigInit().get_conn()
    aa = conn.getOne('select count(*) from download_media')
    pass


def demo_():
    pass


def demo_browser():
    deploy_home = ConfigInit().get_conf().get('DEFAULT', 'deploy_home')
    opts = ChromeOptions()
    # opts.binary_location = '/usr/bin/google-chrome'
    opts.add_argument("--headless")
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    dcap = dict(DesiredCapabilities.CHROME)
    dcap["chrome.page.settings.loadImages"] = False
    chrome_driver = webdriver.Chrome(desired_capabilities=dcap,
                                     executable_path=deploy_home + '/src/config/chromedriver_mac243',
                                     chrome_options=opts)
    chrome_driver.set_page_load_timeout(3)
    try:
        chrome_driver.get('https://www.viki.com/videos/170494v-dream-high-2-episode-5')
    except TimeoutException:
        traceback.print_exc()
    print(chrome_driver.page_source)
    pass


def demo_del_file():
    aa = del_file('/data/tmp/aa.txt')
    pass


def read_files_url():
    urls = [url.replace('\n', '') for url in open('/data/my_ant/play_urls').readlines()]
    # urls = ['https://www.viki.com/videos/133881v-miss-ripley-episode-13']
    demo_controller(random.sample(urls, 1))
    pass


def main():
    # demo_config()
    # demo_stream()
    # demo_controller(['https://www.viki.com/videos/1122394v-stars-lover-episode-11'])
    # demo_mysql()
    # demo_being_download()
    # demo_browser()
    # demo_merge_file()
    # demo_del_file()
    read_files_url()
    pass


if __name__ == '__main__':
    logger.init_log()
    main()
