#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.
import sys

import os
from contextlib import closing

import requests

from src.config import consts
from src.entity.medias import from_string_to_json
from src.tools.ProgressBar import ProgressBar

sys.path.append('../../')
import traceback

import time

from ffmpy import FFmpeg



from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import ChromeOptions


def phantomjs_url_test(url):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
    )
    # dcap["phantomjs.page.settings.loadImages"] = False
    driver = webdriver.PhantomJS(desired_capabilities=dcap,
                                 executable_path='/Users/tv365/phantomjs-2.1.1-macosx/bin/phantomjs')
    # opts = FirefoxOptions()
    # opts.add_argument("--headless")
    # driver = webdriver.Firefox(executable_path=DEPLOY_HOME + '/config/geckodriver_mac', firefox_options=opts)
    # driver._is_remote = False
    # driver.set_page_load_timeout(3)
    try:
        driver.get(url)
    except TimeoutException:
        traceback.print_exc()
    driver.log_types
    logs = driver.get_log('har')
    driver.log_types
    html = driver.execute_script("return document.documentElement.outerHTML")
    embed = driver.find_element_by_xpath("//div[@id='sohuplayer']/embed")
    embed_id = embed.get_attribute('id')
    driver.quit()
    return embed_id


def chrome_test(url):
    opts = ChromeOptions()
    opts.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=DEPLOY_HOME + '/src/config/chromedriver_mac243', chrome_options=opts)
    driver.set_page_load_timeout(15)
    try:
        driver.get(url)
    except TimeoutException:
        traceback.print_exc()
    # scriptToExecute = "var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;"
    # net_work_info = driver.execute_script(scriptToExecute)
    net_work_info = driver.execute_script("return window.performance.getEntries();")
    page_source = driver.page_source.encode('utf-8')
    driver.quit()

    tmp_subtitles_list = parser_subtitles_page_source(page_source)
    subtitles_list = []
    for subtitle in tmp_subtitles_list[:1]:
        subtitle_dict = from_string_to_json(subtitle)
        tmp_subtitle_url = subtitle_dict['src']
        subtitle_dict['source'] = get_subtitle(tmp_subtitle_url)
        subtitles_list.append(subtitle_dict)

    sv_id = url[url.find('videos/') + len('videos/'):url.find('-')]
    net_work_info_str = str(net_work_info)
    begin = net_work_info_str.find('dash_high_480p_') + len('dash_high_480p_')
    sv_play_str = net_work_info_str[begin:net_work_info_str.find('_track', begin)]
    url_video = 'https://content.viki.io/%s/dash/%s_dash_high_480p_%s_track1_dashinit.mp4' % (sv_id, sv_id, sv_play_str)
    url_audio = 'https://content.viki.io/%s/dash/%s_dash_high_480p_%s_track2_dashinit.mp4' % (sv_id, sv_id, sv_play_str)
    down_480p_list = [url_video, url_audio]
    download_video(down_480p_list)
    merge_sv_demo()

    write_file('/Users/tv365/test_de', subtitles_list[0]['source'])
    # subtitles_dict = {'de': '/Users/tv365/test_de'}
    # sv = SingleVideo('vid0', 'svid0', subtitles_dict['de'], '')
    pass


def parser_subtitles_page_source(page_source):
    begin = page_source.find('var subtitles =') + len('var subtitles =')
    end = page_source.find('];', begin)
    tmp_subtitles_list = page_source[begin:end].replace('[', '').replace(' ', '').replace('amp;', '').split('},')
    tmp_subtitles_list = [dict_str + '}' for dict_str in tmp_subtitles_list if '}' not in dict_str]
    return tmp_subtitles_list


def get_subtitle(tmp_subtitle_url):
    opts = ChromeOptions()
    opts.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=DEPLOY_HOME + '/src/config/chromedriver_mac243', chrome_options=opts)
    driver.get(tmp_subtitle_url)
    page_source = driver.page_source.encode('utf-8')
    return page_source


def download_video(down_480p_list):
    begin = time.time()
    for url in down_480p_list:
        if 'track1' in url:
            downloadVideo(url, file_name='test_video')
        else:
            downloadVideo(url, file_name='test_audio')
    end = time.time()
    print('download_over %s' % (end - begin))
    pass


def write_file(save_file, file_buffer):
    with open(save_file, 'w') as f:
        f.write(file_buffer)
    pass


def downloadVideo(url, file_name=''):
    '''
    下载视频
    :param url: 下载url路径
    :return: 文件
    '''
    with closing(requests.get(url, stream=True)) as response:
        chunk_size = 1024
        content_size = int(response.headers['content-length'])
        file_D = '/Users/tv365/' + file_name + '.mp4'
        if (os.path.exists(file_D) and os.path.getsize(file_D) == content_size):
            print('跳过' + file_name)
        else:
            progress = ProgressBar(file_name, total=content_size, unit="KB", chunk_size=chunk_size,
                                   run_status="正在下载", fin_status="下载完成")
            with open(file_D, "wb") as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    progress.refresh(count=len(data))


def merge_sv_demo():
    ff = FFmpeg(inputs={'/Users/tv365/test_video.mp4': '', '/Users/tv365/test_audio.mp4': ''},
                outputs={'/Users/tv365/test_merge.mp4': '-c copy'})
    print(ff.cmd)
    ff.run()
    pass


def main():
    'https://www.viki.com/videos/1138126v-all-out-of-love-episode-3'
    # phantomjs_url_test('https://www.baidu.com')
    chrome_test('https://www.viki.com/videos/1138126v-all-out-of-love-episode-3')
    pass


if __name__ == '__main__':
    main()
