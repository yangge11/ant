#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/13 15:22
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : crawl_viki_demo.py
# @Software: PyCharm
# @ToUse  :
import random
import urllib2

from src.entity.medias import from_string_to_json
from src.tools import consts


def get_paly_urls():
    urls = [
        'https://www.viki.com/tv/31037c-woman-with-a-suitcase',
        'https://www.viki.com/tv/3548c-dream-high-2',
        'https://www.viki.com/tv/35535c-stars-lover',
        'https://www.viki.com/tv/655c-winter-bird',
        'https://www.viki.com/tv/29619c-que-sera-sera',
        'https://www.viki.com/tv/8037c-goodbye-dear-wife',
        'https://www.viki.com/tv/29550c-secret',
        'https://www.viki.com/tv/29465c-my-love-patzzi',
        'https://www.viki.com/tv/12697c-three-days',
        'https://www.viki.com/tv/35530c-bad-couple',
        'https://www.viki.com/tv/29161c-sweet-savage-family',
        'https://www.viki.com/tv/29486c-snowman',
        'https://www.viki.com/tv/29483c-my-lifes-golden-age',
        'https://www.viki.com/tv/31100c-romance-blue',
        'https://www.viki.com/tv/35623c-borg-mom',
        'https://www.viki.com/tv/29473c-who-are-you',
        'https://www.viki.com/tv/28380c-the-virtual-bride',
        'https://www.viki.com/tv/35519c-you-are-too-much',
        'https://www.viki.com/tv/29477c-the-lawyers-of-the-great-republic-of-korea',
        'https://www.viki.com/tv/29546c-air-city',
        'https://www.viki.com/tv/11669c-ad-genius-lee-taebaek',
        'https://www.viki.com/tv/25807c-be-arrogant',
        'https://www.viki.com/tv/29463c-90-days-time-to-love',
        'https://www.viki.com/tv/35571c-daljas-spring',
        'https://www.viki.com/tv/35533c-matchmakers-lover',
        'https://www.viki.com/tv/35539c-women-in-the-sun',
        'https://www.viki.com/tv/35538c-tazza',
        'https://www.viki.com/tv/35532c-surgeon-bong-dal-hee',
        'https://www.viki.com/tv/29545c-general-hospital-2',
        'https://www.viki.com/tv/28243c-28-faces-of-the-moon',
        'https://www.viki.com/tv/25771c-punch',
        'https://www.viki.com/tv/29535c-super-rookie',
        'https://www.viki.com/tv/12068c-the-queen-of-office',
        'https://www.viki.com/tv/26913c-the-man-in-the-mask',
        'https://www.viki.com/tv/29544c-spotlight',
        'https://www.viki.com/tv/3339c-miss-ripley',
        'https://www.viki.com/tv/24873c-boarding-house-24',
        'https://www.viki.com/tv/35542c-sign',
        'https://www.viki.com/tv/29471c-dr-gang',
        'https://www.viki.com/tv/29478c-behind-the-white-tower',
        'https://www.viki.com/tv/35807c-swan',
        'https://www.viki.com/tv/27882c-assembly',
        'https://www.viki.com/tv/35529c-get-karl-oh-soo-jung',
        'https://www.viki.com/tv/27211c-jumping-girl',
        'https://www.viki.com/tv/34053c-bing-goo',
        'https://www.viki.com/tv/28972c-cheers-to-me',
        'https://www.viki.com/tv/29482c-merry-mary',
        'https://www.viki.com/tv/29492c-before-and-after-plastic-surgery-clinic',
        'https://www.viki.com/tv/29666c-puck',
        'https://www.viki.com/tv/29476c-auction-house',
    ]
    play_urls = []
    urls_api = ['https://api.viki.io/v4/containers/%s/episodes.json?sort=number&' \
                'direction=asc&per_page=20&with_paging=true&blocked=true&with_kcp=true&' \
                'app=100000a&page=1' % url[url.find('tv/') + len('tv/'):url.find('-')] for url in urls]
    count = 0
    for url in urls_api:
        count += 1
        print count
        req = urllib2.Request(url=url, headers={'User-Agent': random.choice(consts.constant_manager.USER_AGENTS)})
        response = urllib2.urlopen(req)
        page_source = response.read()
        page_source_json = from_string_to_json(page_source)
        for play_url_dict in page_source_json['response']:
            play_urls.append(play_url_dict['url']['fb'])
    return play_urls


def write_urls(play_urls):
    with open('/data/my_ant/play_urls', 'a') as f:
        for url in play_urls:
            f.write(url + '\n')
    pass


if __name__ == '__main__':
    play_urls = ['1', '2', '3']
    play_urls = get_paly_urls()
    write_urls(play_urls)
