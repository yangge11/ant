#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.

# @Time    : 2018/11/1 14:34
# @Author  : zengyang@tv365.net(ZengYang)
# @File    : bscstorage_tools.py
# @Software: PyCharm
# @ToUse  : 白山云操作

import boto3
from boto3.s3.transfer import TransferConfig

cli = boto3.client(
    's3',
    aws_access_key_id='ziw5dp1alvty9n47qksu',  # 请替换为您自己的access_key
    aws_secret_access_key='V+ZTZ5u5wNvXb+KP5g0dMNzhMeWe372/yRKx4hZV',  # 请替换为您自己的secret_key
    endpoint_url='http://ss.bscstorage.com'
)

resp = cli.put_object(
    ACL='public-read',
    Bucket='test-bucket-xxx',
    Key='test-key-xxx',
    ContentType='image/jpeg',  # 请替换为合适的文件类型
    Body='the content of the file as a string'
)

config = TransferConfig(
    multipart_threshold=30 * 1024 * 1024,
    multipart_chunksize=8 * 1024 * 1024,
    max_concurrency=10
)
resp = cli.upload_file(
    '/root/test.mp4',
    'test-bucket-xxx',
    'test-key-xxx',
    ExtraArgs={
        'ContentType': 'image/jpeg',  # 请替换为合适的文件类型
        'ACL': 'private',
    },
    Config=config
)

resp = cli.get_object(
    Bucket='test-bucket-xxx',
    Key='test-key-xxx'
)

url = cli.generate_presigned_url(
    'get_object',
    Params={
        'Bucket': 'test-bucket-xxx',
        'Key': 'test-key-xxx'
    },
    ExpiresIn=60
)
print url

