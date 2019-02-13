#!/usr/bin/python
# coding=utf8
# Copyright 2017 SARRS Inc. All Rights Reserved.
import sys

sys.path.append('../')
from src.tools.config_manager import ConfigInit
from app.scheduler import scheduler_controller_queue
from flask import Flask, request, jsonify

from src.tools import logger

app = Flask(__name__)


# todo:高并发接口处理
@app.route('/to_controller', methods=['GET'])
def to_controller():
    result_dict = {
        "info": "to_controller",
        "state": "success",
        "url": "",
    }
    if not request.args or 'url' not in request.args:
        result_dict['info'] = 'no url or url is wrong,ip is %s' % request.remote_addr
        result_dict['state'] = 'false'
    scheduler_controller_queue(request.args['url'])
    result_dict['url'] = request.args['url']
    return jsonify(result_dict)


if __name__ == "__main__":
    logger.init_log()
    # 将host设置为0.0.0.0，则外网用户也可以访问到这个服务
    app.run(host=ConfigInit().get_config_by_option('service_ip'), port=1080, debug=True)
