#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/10/23 09:15
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : stream_worker.py
# @Software: PyCharm
# @ToUse  : 截流及下载解析
import copy
import logging
import random
import re
import traceback
import urllib2

import requests
from selenium.common.exceptions import TimeoutException

from src.entity.medias import StreamInfo, from_string_to_json, single_stream_file_json, from_json_to_string
from src.tools import constant_manager, consts
from src.tools.driver_manager import SeleniumDirverFactory, get_driver_test

from settings import support_sites
from src.tools.hash_tools import hash_md5
from src.tools.http_tools import url_decode


def get_and_download_stream_obj(url):
    response_stream, redirect_url = get_old_parsed_info(url)
    if not response_stream:
        for url_pattern in support_sites.keys():
            if url_pattern in redirect_url:
                site_parse_obj = eval(support_sites[url_pattern]['parser'])()
                response_stream = site_parse_obj.parse(redirect_url)
                break
    return response_stream


def get_old_parsed_info(url):
    # todo:稳定获取redirect_url
    try:
        redirect_url = str(
            requests.get(url, headers={'User-Agent': random.choice(consts.constant_manager.USER_AGENTS)},
                         timeout=3).url)
        # todo:已解析過的url緩存判定
        if redirect_url in 'db_sv.urls':
            return '流地址', redirect_url
    except:
        logging.debug('get redirect_url error %s' % url)
        traceback.print_exc()
        redirect_url = url
    return False, redirect_url


def get_media_quality(download_url):
    if '480p' in download_url:
        return consts.constant_manager.MEDIA_480P
    elif '360p' in download_url:
        return consts.constant_manager.MEDIA_360P
    elif '240p' in download_url:
        return consts.constant_manager.MEDIA_240P
    return 'unknown'


class SitesParser(object):
    def __init__(self):
        pass

    def parse(self, url):
        pass

    def build_singel_stream_json(self, download_url, media_type, media_quality='', priority=0, language='',
                                 merged_sign='', merged_order=0):
        new_json = copy.deepcopy(single_stream_file_json)
        new_json['download_url'] = download_url
        new_json['language'] = language
        new_json['priority'] = priority
        new_json['media_type'] = media_type
        new_json['media_quality'] = media_quality
        new_json['merged_sign'] = merged_sign
        new_json['merged_order'] = merged_order
        return new_json

    def log_result(self, subtitle_parse_success, media_parse_success, url):
        if subtitle_parse_success and media_parse_success:
            logging.debug('parse success in %s' % url)
        elif subtitle_parse_success and not media_parse_success:
            logging.warn('parse media fail in %s' % url)
        elif media_parse_success and not subtitle_parse_success:
            logging.warn('parse subtitle fail in %s' % url)
        else:
            logging.error('parse failed in %s' % url)


class VikiParser(SitesParser):
    """
    medias_list:video and audio,240p,360p,480p
    """

    def parse(self, url):
        subtitle_parse_success = media_parse_success = False
        page_source = ''
        net_work_info_list = []
        tmp_subtitles_list = []
        driver_factory = SeleniumDirverFactory()
        driver = driver_factory.get_driver('chrome')
        # page_source, net_work_info_list = get_driver_test(url)
        # todo：使用进程管理浏览器对象，区别管理各个不同的浏览器
        driver.set_page_load_timeout(60 * 3)
        try:
            driver.get(url)
        except TimeoutException:
            logging.debug('time_out load page in %s' % url)
            traceback.print_exc()
        except:
            logging.debug('unknow error in %s' % url)
            traceback.print_exc()
        finally:
            try:
                page_source = driver.page_source.encode('utf-8')
                net_work_info_list = driver.execute_script("return window.performance.getEntries();")
            except:
                logging.debug('unknow error to get page_source in %s' % url)
                traceback.print_exc()
            finally:
                driver_factory.quit_driver('chrome')
                # driver_factory.close_driver()
                logging.debug('quit success')
        # todo:支持付费解析
        if page_source.find('var parsedSubtitles =') != -1:
            begin = page_source.find('var parsedSubtitles =') + len('var parsedSubtitles =')
            end = page_source.find('];', begin)
            tmp_subtitles_str = page_source[begin:end].replace('[', '').replace(' ', '').replace('amp;', '').split('},')
            tmp_subtitles_list = [dict_str + ('}' if '}' not in dict_str else '') for dict_str in tmp_subtitles_str]
        download_file_list = []
        for subtitle in tmp_subtitles_list:
            subtitle_dict = from_string_to_json(subtitle)
            if len(subtitle_dict) == 0:
                continue
            if int(subtitle_dict['percentage']) < 95:
                continue
            download_file_list.append(
                self.build_singel_stream_json(download_url=subtitle_dict['src'], language=subtitle_dict['srclang'],
                                              media_type=constant_manager.SUBTITLE, priority=99))
            subtitle_parse_success = True
        # todo:各清晰度配置,兼容其他类型音视频下载，兼容多段音视频的拼接
        for net_work_dict in net_work_info_list:
            if 'name' in net_work_dict and '480p' in net_work_dict['name'] and 'track' in net_work_dict['name']:
                logging.debug('video and audio parse success')
                media_parse_success = True
                url_video_480p = str(net_work_dict['name']).replace('track2', 'track1')
                url_audio_480p = str(net_work_dict['name']).replace('track1', 'track2')
                download_file_list.append(self.build_singel_stream_json(download_url=url_video_480p,
                                                                        media_quality=consts.constant_manager.MEDIA_480P,
                                                                        media_type=consts.constant_manager.VIDEO,
                                                                        merged_sign='_'.join([url, '480p']),
                                                                        merged_order=1))
                download_file_list.append(
                    self.build_singel_stream_json(download_url=url_audio_480p,
                                                  media_quality=consts.constant_manager.MEDIA_480P,
                                                  media_type=consts.constant_manager.AUDIO,
                                                  merged_sign='_'.join([url, '480p']),
                                                  merged_order=1))
                break
            elif 'name' in net_work_dict and \
                    ('240p' in net_work_dict['name'] or '360p' in net_work_dict['name'] or '480p' in net_work_dict[
                        'name']) \
                    and 'stream_name=' in net_work_dict['name']:
                logging.debug('merged parse success')
                media_parse_success = True
                begin = net_work_dict['name'].find('stream_name=') + len('stream_name=')
                end = net_work_dict['name'].find('&', begin)
                url_merged = url_decode(net_work_dict['name'][begin:end])
                if not url_merged.startswith('http'):
                    logging.error('media url error %s %s' % (url_merged, net_work_dict['name']))
                download_file_list.append(
                    self.build_singel_stream_json(download_url=url_merged,
                                                  media_quality=get_media_quality(url_merged),
                                                  media_type=consts.constant_manager.MERGED, priority=88
                                                  )
                )
                break
        else:
            logging.error('can not find 480p in url %s' % url)
        self.log_result(subtitle_parse_success, media_parse_success, url)
        if len(download_file_list) == 0:
            return from_json_to_string({'info': 'no stream url', 'url': url, 'type': 'error'})
        begin_media_name = page_source.find('<title>') + len('<title>')
        end_media_name = page_source.find('</title>', begin_media_name)
        media_name = page_source[begin_media_name:end_media_name].replace(' ', '')
        begin_video_url = page_source.find('<meta property="video:series" content="') + len(
            '<meta property="video:series" content="')
        end_video_url = page_source.find('"', begin_video_url)
        video_url = page_source[begin_video_url:end_video_url]

        try:
            episode = ''
            episode_begin = media_name.upper().find('EPISODE') + len('EPISODE')
            media_name_with_episode = media_name[episode_begin:]
            episode = re.search('[0-9]+', media_name_with_episode).group(0)
        except:
            traceback.print_exc()
            logging.error('episode error')
        stream_obj = StreamInfo(video_url=video_url, media_name=media_name, episode=episode, original_url=url,
                                download_file_list=download_file_list,
                                site=consts.constant_manager.VIKI, type=consts.constant_manager.DOWNLOAD)
        return stream_obj.from_obj_to_string()

        @staticmethod
        def get_subtitle_content(tmp_subtitle_url):
            # todo：即时url访问处理
            req = urllib2.Request(tmp_subtitle_url)
            req.add_header('User-Agent', random.choice(consts.constant_manager.USER_AGENTS))
            page_source = urllib2.urlopen(req).read()
            return str(page_source)
