#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/10/25 15:13
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : my_demo.py
# @Software: PyCharm
# @ToUse  :
import ConfigParser
import datetime
import json
import logging
import os
import random
import sys

sys.path.append('../')
import paramiko

import tempfile
import threading
import time
import traceback
from selenium.common.exceptions import TimeoutException

from src.dao.download_media_dao import select_tmp, update, select_scp_file, select_original_url_downloaded_subtitle, \
    select_original_url_downloaded_video_audio, select_original_url_downloaded_merged_media
from src.entity.medias import DownloadMedia
from src.tools.driver_manager import SeleniumDirverFactory
from src.tools.file_manager import del_file, get_file_name_by_download_url
from src.tools.hash_tools import hash_md5, get_hash_sign
from src.tools.http_tools import url_decode
from src.worker.monitor_worker import merge_download_media, monitor_download_status

from selenium import webdriver

from app.scheduler import scheduler_controller_queue, scheduler_remote_service, scheduler_db_save_queue
from src.tools.config_manager import ConfigInit
from src.worker.download_worker import Downloader

from selenium.webdriver import ChromeOptions, DesiredCapabilities
from src.tools import consts, logger
from src.tools.queue_manager import RedisMsgQueue
from src.worker.controler_worker import Controller
from src.worker.worker import Worker
from unit_test.crawl_viki_demo import get_paly_urls, write_urls


def demo_config():
    conf = ConfigParser.ConfigParser()
    conf.read('/Users/tv365/code/ant/src/config/deploy.ini')
    pass


def demo_controller(urls):
    for url in urls:
        scheduler_controller_queue(url)
    task_queue = RedisMsgQueue()
    controller_worker = Controller(consts.constant_manager.CONTROLLER_QUEUE_NAME, task_queue, 1)
    controller_worker.start()
    controller_worker.wait()
    task_queue.addQueue(consts.constant_manager.DOWNLOAD_QUEUE_NAME, 20480)
    task_queue.addQueue('demo', 20480)
    # downloader_worker = Downloader(consts.constant_manager.DOWNLOAD_QUEUE_NAME, task_queue, 1)
    # downloader_worker.start()
    # downloader_worker.wait()
    downloader_worker = Downloader('demo', task_queue, 1)
    downloader_worker.start()
    downloader_worker.wait()
    # task_queue = RedisMsgQueue()
    # controller_worker = Controller(consts.constant_manager.CONTROLLER_QUEUE_NAME, task_queue, 1)
    # controller_worker.start()
    while True:
        logging.info("=================> queue_size: %d",
                     task_queue.size(consts.constant_manager.CONTROLLER_QUEUE_NAME))
        time.sleep(10)
    pass


def demo_merge_file():
    merge_download_media()
    pass


def demo_being_download():
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
    # 删除本地下载国产剧
    urls = [url.replace('\n', '') for url in open('/data/my_ant/play_urls1')]
    sql = """
    SELECT absolute_path FROM crawler_online.download_media where download_status=1 and download_path='/data/dev_ant/' and 
    original_url in (%s);
    """ % ', '.join(map(lambda x: "'%s'" % x, urls))
    client = ConfigInit().get_conn()
    all_tuple = client.getAll(sql)
    dalu_files_local = [url_dict['absolute_path'] for url_dict in all_tuple] if all_tuple else []
    for file in dalu_files_local:
        try:
            if os.path.exists(file):
                del_file(file)
        except:
            traceback.print_exc()
    pass


def demo_files_url():
    # urls = [url.replace('\n', '') for url in open('/data/my_ant/play_urls').readlines()]
    urls = ['https://www.viki.com/videos/1117962v-the-lovers-lies-episode-3']
    # demo_controller(random.sample(urls, 10))
    scheduler_remote_service(urls)
    # demo_controller(urls[:10])
    pass


def download_all():
    play_urls = get_paly_urls()
    write_urls(play_urls)
    # scheduler_remote_service(play_urls)
    pass


def demo_worker_exception():
    task_queue = RedisMsgQueue()
    task_queue.addQueue(consts.constant_manager.CONTROLLER_QUEUE_NAME, 20480)
    for i in range(1, 100):
        task_queue.push(consts.constant_manager.CONTROLLER_QUEUE_NAME, 'asdasdas')
    worker = Worker(consts.constant_manager.CONTROLLER_QUEUE_NAME, task_queue, 3)
    worker.start()
    while True:
        print 'demo'
        time.sleep(30)
    pass


def demo_chrome_memory():
    for i in range(1, 2):
        driver = SeleniumDirverFactory().get_driver('chrome')
        # todo：稳定性处理
        driver.set_page_load_timeout(3)
        try:
            driver.get('https://www.viki.com/tv/655c-winter-bird#modal-episode')
        except TimeoutException:
            traceback.print_exc()
        finally:
            page_source = driver.page_source.encode('utf-8')
            net_work_info_list = driver.execute_script("return window.performance.getEntries();")
            SeleniumDirverFactory().quit_driver('chrome')
            # try:
            #     page_source = driver.page_source.encode('utf-8')
            #     net_work_info_list = driver.execute_script("return window.performance.getEntries();")
            # except:
            #     traceback.print_exc()
            # finally:
            #     SeleniumDirverFactory().quit_driver('chrome')
    pass


def get_miss_play_url():
    urls = [url.replace('\n', '') for url in open('/data/my_ant/play_urls').readlines()]
    sql = """
    
    """
    pass


def demo_url():
    url = 'https%3a%2f%2fv.viki.io%2f1083325v%2f1083325v_high_480p_1510140944.mp4%3fe%3d1542789430%26h%3d047a4e151ba010c7f257a116fcea2fae'
    aa = url_decode(url)
    pass


def rename_file():
    # 1.查询文件名称；2.根据相应的数据，确认计算出要修改的名称及对应的hash值
    logging.debug('begin')
    aa = list(select_tmp())
    for dict in aa:
        try:
            id_media = 'no_id'
            file_name = get_file_name_by_download_url(dict['download_url'])
            if dict['media_type'] == consts.constant_manager.SUBTITLE:
                file_name = 'viki' + '_' + get_file_name_by_download_url(dict['original_url']) + \
                            '_' + dict['language']
            dict['new_absolute_path'] = '/data/dev_ant/' + file_name + '.' + dict['file_type']
            dict['new_hash_sign'] = get_hash_sign(file_name)
            # 重命名文件
            os.rename(dict['absolute_path'], dict['new_absolute_path'])
            # 写库操作
            id_media = dict['id']
            download_media_json = {
                'id': id_media,
                'hash_sign': get_hash_sign(file_name),
                'absolute_path': dict['new_absolute_path'],
            }
            update(DownloadMedia().from_json_to_obj(download_media_json))
            logging.debug('update success id %s' % dict['id'])
        except:
            traceback.print_exc()
            logging.error('update error id %s' % id_media)
        pass
    pass


def del_downnload_files():
    scp_files = list(select_scp_file())
    # for absolute_path in scp_files:
    #     try:
    #         del_file(absolute_path)
    #     except:
    #         traceback.print_exc()
    pass


def demo_chrome():
    import time
    from selenium import webdriver
    import selenium.webdriver.chrome.service as service
    service = service.Service('/Users/tv365/code/ant/src/config/chromedriver_mac243')
    service.start()
    # capabilities = {'chrome.binary': '/path/to/custom/chrome'}
    # driver = webdriver.Remote(service.service_url, capabilities)
    urls = [url.replace('\n', '') for url in open('/data/my_ant/play_urls').readlines()]
    for i, url in enumerate(random.sample(urls, 10)):
        opts = ChromeOptions()
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        dcap = dict(DesiredCapabilities.CHROME)
        dcap["chrome.page.settings.loadImages"] = False
        opts.add_argument("--headless")
        driver = webdriver.Remote(service.service_url, options=opts, desired_capabilities=dcap)
        driver.get('http://www.google.com/xhtml')
        time.sleep(5)  # Let the user actually see something!
        driver.save_screenshot(str(i) + '.png')
        driver.quit()
    pass


def scp_file():
    aa = select_scp_file()
    '/data/dev_ant/viki_1112337v-woman-with-a-suitcase-episode-1_en.txt'
    pass


def demo_redis():
    redis_queue = RedisMsgQueue()
    aa = redis_queue.hash_get_all(consts.constant_manager.DOWNLOAD_STATUS_QUEUE_NAME)
    pass


def demo_queue():
    redis_queue = RedisMsgQueue()
    aa = redis_queue.hash_del(consts.constant_manager.DOWNLOAD_STATUS_QUEUE_NAME, '748ffc2387967c2d0ec518516239ea42')
    pass


def demo_time():
    all_json_tmp = [text for text in open('/data/tmp/1.log')][0]
    begin = all_json_tmp.find('text_body:') + len('text_body:')
    end = all_json_tmp.find(', req_id:')
    all_json = json.loads(all_json_tmp[begin:end])
    time = all_json['time']
    stamp = all_json['data']['qcdn.yingshidq.com.cn']['china']
    end_json = {}
    for index, time_key in enumerate(time):
        end_json[time_key] = stamp[index]
    print end_json


def demo_monitor_download_status():
    monitor_download_status()
    pass


def demo_tmp():
    aa = time.time()
    time.sleep(3)
    a1 = time.time()
    pass


def demo_failed_urls():
    logging.debug('start re_crawl urls')
    urls = get_paly_urls()
    write_urls(urls)
    urls = [url.replace('\n', '') for url in open('/data/my_ant/play_urls').readlines()]
    urls_downloaded_subtitle = select_original_url_downloaded_subtitle(urls)
    urls_downloaded_media = select_original_url_downloaded_video_audio(urls)
    urls_downloaded_merged_media = select_original_url_downloaded_merged_media(urls)
    urls_to_parse_subtitle = set(urls) - set(urls_downloaded_subtitle)
    urls_to_parse_media = set(urls) - set(urls_downloaded_media) - set(urls_downloaded_merged_media)
    urls_to_parse = urls_to_parse_subtitle | urls_to_parse_media
    for url in urls_to_parse:
        # scheduler_remote_service(urls_to_parse)
        scheduler_controller_queue(url)
    pass


def demo1():
    pass


def main():
    # demo_tmp()
    # demo_config()
    # demo_stream()
    demo_controller(['https://www.viki.com/videos/1101534v-school-beautys-personal-bodyguard-episode-2'])
    # demo_mysql()
    # demo_being_download()
    # demo_browser()
    # demo_merge_file()
    # demo_del_file()
    # demo_files_url()
    # download_all()
    # demo_worker_exception()
    # demo_chrome_memory()
    # demo_url()
    # rename_file()
    # demo_chrome()
    # del_downnload_files()
    # demo_redis()
    # demo_queue()
    # demo_monitor_download_status()
    # demo_failed_urls()
    pass


if __name__ == '__main__':
    logger.init_log()
    main()
    # demo_time()
