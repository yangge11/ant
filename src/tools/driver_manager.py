#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.
import ConfigParser
import logging
import random
import threading
import signal
import traceback

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import DesiredCapabilities, chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver import FirefoxOptions
from src.tools import consts
from src.tools.config_manager import ConfigInit
from src.tools.hash_tools import hash_md5


def get_driver_test(url):
    page_source = net_work_info_list = []
    service = chrome.service.Service('/Users/tv365/code/ant/src/config/chromedriver_mac243')
    service.start()
    # capabilities = {'chrome.binary': '/path/to/custom/chrome'}
    # driver = webdriver.Remote(service.service_url, capabilities)
    opts = ChromeOptions()
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    dcap = dict(DesiredCapabilities.CHROME)
    dcap["chrome.page.settings.loadImages"] = False
    opts.add_argument("--headless")
    PROXY = '97.64.40.68:10086'
    dcap['proxy'] = {
        "httpProxy": PROXY,
        "ftpProxy": PROXY,
        "sslProxy": PROXY,
        "noProxy": None,
        "proxyType": "MANUAL",
        "class": "org.openqa.selenium.Proxy",
        "autodetect": False
    }
    driver = webdriver.Remote(service.service_url, options=opts, desired_capabilities=dcap)
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
            driver.get_screenshot_as_file(hash_md5(url) + '.png')
        except:
            logging.debug('unknow error to get page_source in %s' % url)
            traceback.print_exc()
        finally:
            # driver_factory.quit_driver('chrome')
            driver.quit()
            logging.debug('quit success')
    return page_source, net_work_info_list


class SeleniumDirverFactory(object):
    _instance_lock = threading.Lock()
    _driver = {}

    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(SeleniumDirverFactory, "_instance"):
    #         with SeleniumDirverFactory._instance_lock:
    #             if not hasattr(SeleniumDirverFactory, "_instance"):
    #                 SeleniumDirverFactory._instance = object.__new__(cls)
    #     return SeleniumDirverFactory._instance

    def __init__(self):
        pass

    def get_driver(self, name='chrome', type='headless'):
        # todo:内存泄漏问题；各个浏览器配置管理
        deploy_home = ConfigInit().get_conf().get('DEFAULT', 'deploy_home')
        if name == 'phantomjs':
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = (random.choice(consts.USER_AGENTS))
            dcap["phantomjs.page.settings.loadImages"] = False
            driver_phantomjs = webdriver.PhantomJS(desired_capabilities=dcap,
                                                   executable_path=deploy_home + '/src/config/phantomjs')
            self._driver[name] = driver_phantomjs
        elif name == 'chrome':
            opts = ChromeOptions()
            opts.add_argument('--no-sandbox')
            opts.add_argument('--disable-dev-shm-usage')
            # opts.add_argument('--proxy-server=http://97.64.40.68:10086')
            dcap = dict(DesiredCapabilities.CHROME)
            dcap["chrome.page.settings.loadImages"] = False
            # PROXY = '97.64.40.68:10086'
            # dcap['proxy'] = {
            #     "httpProxy": PROXY,
            #     "ftpProxy": PROXY,
            #     "sslProxy": PROXY,
            #     "noProxy": None,
            #     "proxyType": "MANUAL",
            #     "class": "org.openqa.selenium.Proxy",
            #     "autodetect": False
            # }
            if type == 'headless':
                opts.add_argument("--headless")
            chrome_driver = webdriver.Chrome(desired_capabilities=dcap,
                                             executable_path=deploy_home + ConfigInit().get_config_by_option(
                                                 'chrome_path'),
                                             chrome_options=opts)
            self._driver[name] = chrome_driver
        elif name == 'firefox':
            opts = FirefoxOptions()
            if type == 'headless':
                opts.add_argument("--headless")
            firefox_driver = webdriver.Firefox(executable_path=deploy_home + '/src/config/geckodriver_mac',
                                               firefox_options=opts)
            self._driver[name] = firefox_driver
        return self._driver[name]

    def close_driver(self, name='chrome'):
        # todo:暂时关闭会导致driver用不了,目前只测试了phantomjs
        if name not in self._driver.keys():
            # todo：分离的日志系统使用
            logging.debug('no %s driver create error' % name)
            return
        try:
            self._driver[name].close()
        except:
            traceback.print_exc()
            logging.error('close page error')
            pass
        pass

    def quit_driver(self, name='chrome'):
        # with self._instance_lock:
        #     try:
        #         if name not in self._driver.keys():
        #             # todo：分离的日志系统使用
        #             logging.debug('no %s driver create error' % name)
        #             return
        #         # driver.close() and driver.quit() killed the node process but not the phantomjs child process it spawned
        #         self._driver[name].service.process.send_signal(signal.SIGTERM)  # kill the specific phantomjs child proc
        #         self._driver[name].quit()  # quit the node proc
        #         self._driver.pop(name)
        #     except OSError:
        #         traceback.print_exc()
        #         logging.error('quit driver os error')
        #     except:
        #         traceback.print_exc()
        #         logging.error('quit driver error')
        try:
            if name not in self._driver.keys():
                # todo：分离的日志系统使用
                logging.debug('no %s driver create error' % name)
                return
            # driver.close() and driver.quit() killed the node process but not the phantomjs child process it spawned
            # self._driver[name].service.process.send_signal(signal.SIGTERM)  # kill the specific phantomjs child proc
            self._driver[name].quit()  # quit the node proc
        except OSError:
            traceback.print_exc()
            logging.error('quit driver os error')
        except:
            traceback.print_exc()
            logging.error('quit driver error')
