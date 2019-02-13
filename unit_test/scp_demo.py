#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/25 17:30
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : scp_demo.py
# @Software: PyCharm
# @ToUse  :
import logging
import os
import sys
import thread
import threading
import time
import traceback
sys.path.append('../')
import paramiko

from src.dao.download_media_dao import select_scp_file
from src.tools import logger

download_over_files = select_scp_file()
has_in_local_files = os.listdir('/data/dev_ant')
has_in_local_absolute_files = ['/data/dev_ant/' + file_name for file_name in has_in_local_files]
to_scp_files = list(set(download_over_files) - set(has_in_local_absolute_files))


def ssh_scp_put(ip, port, user, password, local_file, remote_file):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, 22, 'root', password)
    a = ssh.exec_command('date')
    stdin, stdout, stderr = a
    print stdout.read()
    sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
    sftp = ssh.open_sftp()
    sftp.put(local_file, remote_file)


def ssh_scp_get(thread_name, ip, port, user, password):
    while len(to_scp_files) > 0:
        try:
            file = to_scp_files.pop()
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, 22, 'root', password)
            a = ssh.exec_command('date')
            stdin, stdout, stderr = a
            print stdout.read()
            sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
            sftp = ssh.open_sftp()
            sftp.get(file, file.replace('/data/dev_ant/', '/data/tmp/'))
            logging.debug('write file over')
        except:
            traceback.print_exc()
            logging.error('except file is %s' % file)
        finally:
            ssh.close()
    logging.debug('thread over')


def download_files_to_local():
    for i in range(20):
        thread.start_new_thread(ssh_scp_get, ('thread_' + str(i), '128.1.41.120', 22, 'root', '6DVheiVs'))
    while True:
        logging.debug('main running')
        time.sleep(30)
    pass


def main():
    download_files_to_local()
    # ssh_scp_get('128.1.41.120', 22, 'root', '6DVheiVs',
    #             '/data/dev_ant/1098249v_high_480p_1603070738_track1_dashinit.mp4',
    #             '/data/dev_ant/1098249v_high_480p_1603070738_track1_dashinit.mp4')
    pass


if __name__ == '__main__':
    logger.init_log()
    main()
