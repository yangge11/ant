#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/13 15:22
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : crawl_viki_demo.py
# @Software: PyCharm
# @ToUse  :
import logging
import random
import traceback
import urllib2

from src.entity.medias import from_string_to_json
from src.tools import consts


def get_paly_urls():
    urls_support = [
        # 韩剧
        # 'https://www.viki.com/tv/31037c-woman-with-a-suitcase',
        # 'https://www.viki.com/tv/3548c-dream-high-2',
        # 'https://www.viki.com/tv/8037c-goodbye-dear-wife',
        # 'https://www.viki.com/tv/29550c-secret',
        # 'https://www.viki.com/tv/29465c-my-love-patzzi',
        # 'https://www.viki.com/tv/29161c-sweet-savage-family',
        # 'https://www.viki.com/tv/29486c-snowman',
        # 'https://www.viki.com/tv/29483c-my-lifes-golden-age',
        # 'https://www.viki.com/tv/31100c-romance-blue',
        # 'https://www.viki.com/tv/35623c-borg-mom',
        # 'https://www.viki.com/tv/29473c-who-are-you',
        # 'https://www.viki.com/tv/29546c-air-city',
        # 'https://www.viki.com/tv/25807c-be-arrogant',
        # 'https://www.viki.com/tv/29463c-90-days-time-to-love',
        # 'https://www.viki.com/tv/29545c-general-hospital-2',
        # 'https://www.viki.com/tv/28243c-28-faces-of-the-moon',
        # 'https://www.viki.com/tv/29535c-super-rookie',
        # 'https://www.viki.com/tv/26913c-the-man-in-the-mask',
        # 'https://www.viki.com/tv/29544c-spotlight',
        # 'https://www.viki.com/tv/3339c-miss-ripley',
        # 'https://www.viki.com/tv/24873c-boarding-house-24',
        # 'https://www.viki.com/tv/29471c-dr-gang',
        # 'https://www.viki.com/tv/29478c-behind-the-white-tower',
        # 'https://www.viki.com/tv/35807c-swan',
        # 'https://www.viki.com/tv/27211c-jumping-girl',
        # 'https://www.viki.com/tv/28972c-cheers-to-me',
        # 'https://www.viki.com/tv/29482c-merry-mary',
        # 'https://www.viki.com/tv/29492c-before-and-after-plastic-surgery-clinic',
        # 'https://www.viki.com/tv/29666c-puck',
        # # 大陆
        # 'https://www.viki.com/tv/29015c-my-sunshine-directors-cut',
        # 'https://www.viki.com/tv/21925c-singing-all-along',
        # 'https://www.viki.com/tv/28160c-the-interpreter',
        # 'https://www.viki.com/tv/35697c-an-oriental-odyssey',
        # 'https://www.viki.com/tv/29908c-fifteen-years-of-waiting-for-migratory-birds',
        # 'https://www.viki.com/tv/36049c-sweet-dreams',
        # 'https://www.viki.com/tv/31805c-because-of-meeting-you',
        # 'https://www.viki.com/tv/31618c-princess-agents',
        # 'https://www.viki.com/tv/35699c-sweet-combat',
        # 'https://www.viki.com/tv/36178c-ever-night',
        # 'https://www.viki.com/tv/35601c-dear-prince',
        # 'https://www.viki.com/tv/35857c-secret-of-the-three-kingdoms',
        # 'https://www.viki.com/tv/32658c-the-foxs-summer',
        # 'https://www.viki.com/tv/35576c-the-foxs-summer-season-2',
        # 'https://www.viki.com/tv/29266c-love-me-if-you-dare',
        # 'https://www.viki.com/tv/33387c-pretty-li-hui-zhen',
        # 'https://www.viki.com/tv/33973c-my-mr-mermaid',
        # 'https://www.viki.com/tv/31583c-my-amazing-boyfriend',
        # 'https://www.viki.com/tv/35710c-i-cannot-hug-you',
        # 'https://www.viki.com/tv/35684c-face-off',
        # 'https://www.viki.com/tv/23841c-the-imperial-doctress',
        # 'https://www.viki.com/tv/34371c-the-kings-woman',
        # 'https://www.viki.com/tv/30283c-song-of-phoenix',
        # 'https://www.viki.com/tv/36044c-the-love-knot-his-excellencys-first-love',
        # 'https://www.viki.com/tv/21864c-chinese-paladin-5-clouds-of-the-world',
        # 'https://www.viki.com/tv/22943c-nirvana-in-fire',
        # 'https://www.viki.com/tv/35605c-the-flames-daughter',
        # 'https://www.viki.com/tv/25705c-legend-of-lu-zhen',
        # 'https://www.viki.com/tv/35664c-fighter-of-the-destiny',
        # 'https://www.viki.com/tv/29384c-whirlwind-girl',
        # 'https://www.viki.com/tv/30332c-the-legend-of-chusen',
        # 'https://www.viki.com/tv/35843c-siege-in-fog',
        # 'https://www.viki.com/tv/20346c-perfect-couple',
        # 'https://www.viki.com/tv/22353c-daughter-back',
        # 'https://www.viki.com/tv/30705c-addicted',
        # 'https://www.viki.com/tv/35607c-delicious-destiny',
        # 'https://www.viki.com/tv/28842c-ice-fantasy',
        # 'https://www.viki.com/tv/23849c-thinking-of-you-lu-xiang-bei',
        # 'https://www.viki.com/tv/21228c-legend-of-the-ancient-sword',
        # 'https://www.viki.com/tv/33665c-across-the-ocean-to-see-you',
        # 'https://www.viki.com/tv/32827c-nirvana-in-fire-2',
        # 'https://www.viki.com/tv/30299c-hot-girl',
        # 'https://www.viki.com/tv/34161c-love-just-come',
        # 'https://www.viki.com/tv/2978c-scarlet-heart',
        # 'https://www.viki.com/tv/31190c-when-a-snail-falls-in-love',
        # 'https://www.viki.com/tv/12472c-the-four',
        # 'https://www.viki.com/tv/35704c-only-side-by-side-with-you',
        # 'https://www.viki.com/tv/28818c-my-best-ex-boyfriend',
        # 'https://www.viki.com/tv/12747c-scarlet-heart-2',
        # 'https://www.viki.com/tv/34436c-the-lovers-lies',
        # 日剧
        # 'https://www.viki.com/tv/35651c-youre-my-pet-kimi-wa-petto',
        # 'https://www.viki.com/tv/31884c-sunshine',
        # 'https://www.viki.com/tv/29377c-my-little-lover-minami-kun-no-koibito',
        # 'https://www.viki.com/tv/35654c-hakuouki-ssl-sweet-school-life',
        # 'https://www.viki.com/tv/31882c-rainbow-rose',
        # 'https://www.viki.com/tv/31813c-vampire-heaven',
        # 'https://www.viki.com/tv/29394c-lady-girls',
        # 'https://www.viki.com/tv/35653c-i-am-reiko-shiratori-shiratori-reiko-de-gozaimasu',
        # 'https://www.viki.com/tv/34349c-delicious-niigata-in-japan',
        # 'https://www.viki.com/tv/36303c-iniesta-tv',
        # 'https://www.viki.com/tv/23069c-love-stories-from-fukuoka',
        # 'https://www.viki.com/tv/28765c-visiting-sacred-places-of-the-tohoku-region',
        # 'https://www.viki.com/tv/31798c-blue-fire',
        # 'https://www.viki.com/tv/7468c-leiji-matsumotos-ozma',
        # 'https://www.viki.com/tv/34350c-railway-story',
        # 'https://www.viki.com/tv/36253c-iniesta-tv-discover-japan',
        # 'https://www.viki.com/tv/36302c-iniesta-tv-interviews',
        # 'https://www.viki.com/tv/29122c-tabiaruki-from-iwate',
        # 'https://www.viki.com/tv/33804c-a-heartfelt-trip-to-fukushima',
        # 'https://www.viki.com/tv/33807c-lets-explore-fukushima',
        # 'https://www.viki.com/tv/33806c-murakami-grand-festival-2016-tradition-passed-down',
        # 'https://www.viki.com/tv/33805c-festival-pride-for-hometown',
        # 'https://www.viki.com/tv/30268c-sendai-iroha-zoukangou',
        # 'https://www.viki.com/tv/34348c-the-sanjo-great-kite-battle',
        # 'https://www.viki.com/tv/36085c-vissel-kobe-welcome-event-bienvenido-andrs-iniesta',
        # 'https://www.viki.com/tv/34345c-tales-of-tohoku',
        # 台剧
        'https://www.viki.com/tv/29014c-crime-scene-investigation-center',
        'https://www.viki.com/tv/36219c-campus-heroes',
        'https://www.viki.com/tv/36106c-love-and',
        'https://www.viki.com/tv/35897c-my-little-boys',
        'https://www.viki.com/tv/35859c-between',
        'https://www.viki.com/tv/35830c-single-ladies-senior',
        'https://www.viki.com/tv/35712c-iron-ladies',
        'https://www.viki.com/tv/35708c-see-you-in-time',
        'https://www.viki.com/tv/35627c-lulus-diary',
        'https://www.viki.com/tv/35561c-home-sweet-home',
        'https://www.viki.com/tv/35560c-memory-love',
        'https://www.viki.com/tv/35552c-when-a-woman-chases-a-man',
        'https://www.viki.com/tv/35551c-attention-love',
        'https://www.viki.com/tv/35549c-lion-pride',
        'https://www.viki.com/tv/35492c-the-man-from-the-future',
        'https://www.viki.com/tv/34532c-the-masked-lover',
        'https://www.viki.com/tv/34531c-the-perfect-match',
        'https://www.viki.com/tv/34530c-just-for-you',
        'https://www.viki.com/tv/33719c-all-in-700',
        'https://www.viki.com/tv/33590c-behind-your-smile',
        'https://www.viki.com/tv/33551c-the-king-of-romance',
        'https://www.viki.com/tv/33362c-v-focus',
        'https://www.viki.com/tv/32673c-love-by-design',
        'https://www.viki.com/tv/32353c-27th-golden-melody-awards',
        'https://www.viki.com/tv/32310c-swimming-battle',
        'https://www.viki.com/tv/32029c-better-man',
        'https://www.viki.com/tv/31402c-metro-of-love',
        'https://www.viki.com/tv/30921c-love-at-seventeen',
        'https://www.viki.com/tv/30868c-spop-weekly-report',
        'https://www.viki.com/tv/30410c-back-to-1989',
        'https://www.viki.com/tv/30017c-be-with-me',
        'https://www.viki.com/tv/29959c-thirty-something',
        'https://www.viki.com/tv/29705c-love-or-spend',
        'https://www.viki.com/tv/29259c-bromance',
        'https://www.viki.com/tv/23561c-love-myself-or-you',
        'https://www.viki.com/tv/28856c-school-beautys-personal-bodyguard',
        'https://www.viki.com/tv/28009c-when-i-see-you-again',
        'https://www.viki.com/tv/27213c-murphys-law-of-love',
        'https://www.viki.com/tv/20292c-just-you',
        'https://www.viki.com/tv/20331c-love-around',
        'https://www.viki.com/tv/635c-autumns-concerto',
        'https://www.viki.com/tv/228c-fated-to-love-you',
        'https://www.viki.com/tv/26885c-shia-wa-se',
        'https://www.viki.com/tv/23266c-fall-in-love-with-me',
    ]
    play_urls = []
    urls_api = ['https://api.viki.io/v4/containers/%s/episodes.json?sort=number&' \
                'direction=asc&per_page=200&with_paging=true&blocked=true&with_kcp=true&' \
                'app=100000a&page=1' % url[url.find('tv/') + len('tv/'):url.find('-')] for url in urls_support]
    count = 0
    for url in urls_api:
        try:
            count += 1
            logging.debug(count)
            req = urllib2.Request(url=url, headers={'User-Agent': random.choice(consts.constant_manager.USER_AGENTS)})
            response = urllib2.urlopen(req)
            page_source = response.read()
            page_source_json = from_string_to_json(page_source)
            for play_url_dict in page_source_json['response']:
                play_urls.append(play_url_dict['url']['fb'])
        except:
            traceback.print_exc()
    return play_urls


def write_urls(play_urls):
    with open('/data/my_ant/play_urls', 'w') as f:
        for url in play_urls:
            f.write(url + '\n')
    pass


if __name__ == '__main__':
    play_urls = ['1', '2', '3']
    play_urls = get_paly_urls()
    write_urls(play_urls)
