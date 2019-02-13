#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/16 17:09
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : demo_process_thread.py
# @Software: PyCharm
# @ToUse  :


import os
import sys
import threading
import traceback
import signal
import tempfile
from datetime import datetime
import time


def test():
    while True:
        print datetime.now()
        time.sleep(2)


def signal_handler(signum, frame):
    try:
        print '---'
        result = []
        result.append("*** STACKTRACE - START ***\n")

        threads = threading.enumerate()
        for thread in threads:
            stack = sys._current_frames()[thread.ident]
            result.append("\nThread ID: %s, Name: %s\n" % (thread.ident, thread.name))
            for filename, line_no, name, line in traceback.extract_stack(stack):
                result.append('  "%s", line %d, in %s\n' % (filename, line_no, name))
                if line:
                    result.append("    %s\n" % (line.strip()))

        result.append("\n*** STACKTRACE - END ***\n")

        file = os.path.join(tempfile.gettempdir(), datetime.now().strftime('%Y%m%d%H%M%S') + ".log")
        with open(file, 'w+') as f:
            f.writelines(result)
    except BaseException as e:
        print e


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGQUIT, signal_handler)

        threading.Thread(target=test).start()

        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        sys.exit(1)