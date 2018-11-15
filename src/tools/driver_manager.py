#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.
import ConfigParser
import random
import threading
import signal
import traceback
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver import ChromeOptions
from selenium.webdriver import FirefoxOptions

# todo:各类浏览器的管理
# 正确做法应该是本服务提供一个driver的稳定生产和销毁，监控driver进程，防止内存泄漏
from src.tools import consts
from src.tools.config_manager import ConfigInit


class SeleniumDirverFactory(object):
    _instance_lock = threading.Lock()
    _driver = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(SeleniumDirverFactory, "_instance"):
            with SeleniumDirverFactory._instance_lock:
                if not hasattr(SeleniumDirverFactory, "_instance"):
                    SeleniumDirverFactory._instance = object.__new__(cls)
        return SeleniumDirverFactory._instance

    def __init__(self):
        pass

    def get_driver(self, name='chrome', type='headless'):
        # todo:内存泄漏问题；各个浏览器配置管理
        self._instance_lock.acquire()
        if name in self._driver.keys():
            return self._driver[name]
        self._instance_lock.release()
        deploy_home = ConfigInit().get_conf().get('DEFAULT', 'deploy_home')
        if name == 'phantomjs':
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = (random.choice(consts.USER_AGENTS))
            dcap["phantomjs.page.settings.loadImages"] = False
            driver_phantomjs = webdriver.PhantomJS(desired_capabilities=dcap,
                                                   executable_path=deploy_home + '/src/config/phantomjs')
            self._driver[name] = driver_phantomjs
            return driver_phantomjs
        elif name == 'chrome':
            opts = ChromeOptions()
            opts.add_argument('--no-sandbox')
            opts.add_argument('--disable-dev-shm-usage')
            dcap = dict(DesiredCapabilities.CHROME)
            dcap["chrome.page.settings.loadImages"] = False
            if type == 'headless':
                opts.add_argument("--headless")
            chrome_driver = webdriver.Chrome(desired_capabilities=dcap,
                                             executable_path=deploy_home + ConfigInit().get_config_by_option(
                                                 'chrome_path'),
                                             chrome_options=opts)
            self._driver[name] = chrome_driver
            return chrome_driver
        elif name == 'firefox':
            opts = FirefoxOptions()
            if type == 'headless':
                opts.add_argument("--headless")
            firefox_driver = webdriver.Firefox(executable_path=deploy_home + '/src/config/geckodriver_mac',
                                               firefox_options=opts)
            self._driver[name] = firefox_driver
            return firefox_driver

    def close_driver(self, name='chrome'):
        with self._instance_lock:
            # todo:暂时关闭会导致driver用不了,目前只测试了phantomjs
            if name not in self._driver.keys():
                # todo：分离的日志系统使用
                traceback.print_exc('no %s driver create error' % name)
                return
            self._driver[name].close()
        pass

    def quit_driver(self, name='chrome'):
        with self._instance_lock:
            if name not in self._driver.keys():
                # todo：分离的日志系统使用
                traceback.print_exc('no %s driver create error' % name)
                return
            # driver.close() and driver.quit() killed the node process but not the phantomjs child process it spawned
            self._driver[name].service.process.send_signal(signal.SIGTERM)  # kill the specific phantomjs child proc
            try:
                self._driver[name].quit()  # quit the node proc
                self._driver.pop(name)
            except OSError:
                traceback.print_exc()
            except:
                traceback.print_exc()
        pass
