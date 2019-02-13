#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/12/7 16:33
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : demo_service.py
# @Software: PyCharm
# @ToUse  : 服务器端各种功能型测试
import random
import traceback

from flask import request, Flask
from flask.json import jsonify
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions, DesiredCapabilities

app = Flask(__name__)


def demo_browser():
    opts = ChromeOptions()
    # opts.binary_location = '/usr/bin/google-chrome'
    opts.add_argument("--headless")
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    dcap = dict(DesiredCapabilities.CHROME)
    dcap["chrome.page.settings.loadImages"] = False
    chrome_driver = webdriver.Chrome(desired_capabilities=dcap,
                                     executable_path='/test/chromedriver_linux243',
                                     chrome_options=opts)
    chrome_driver.set_page_load_timeout(60)
    try:
        chrome_driver.get('https://www.viki.com/videos/170494v-dream-high-2-episode-5')
    except TimeoutException:
        traceback.print_exc()
    print(chrome_driver.page_source)


@app.route('/to_controller', methods=['GET'])
def to_controller():
    print 'success in'
    result_dict = {
        "info": "to_controller",
        "state": "success",
        "url": "",
    }
    if not request.args or 'url' not in request.args:
        result_dict['info'] = 'no url or url is wrong,ip is %s' % request.remote_addr
        result_dict['state'] = 'false'
    result_dict['url'] = request.args['url']
    return jsonify(result_dict)


def demo_request():
    app.run(host='127.0.0.1', port=1080, debug=True)
    pass


def main():
    demo_browser()
    # demo_request()
    pass


if __name__ == '__main__':
    main()
