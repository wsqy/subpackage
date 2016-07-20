#!/bin/env python2.7
# coding:utf-8

import os
import gevent
import settings
from messageNotice import Message
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('mylogger')

class Upload:
    def __init__(self):
        self.upload_subpackage_dict = {}
        self.no_task_sleep_time = settings.no_task_sleep_time
        self.message = Message()

    def get_upload_info(self, response, notice_url):
        filename = response.get_filename()
        self.upload_subpackage_dict[filename] = [len(settings.storageList), notice_url, []]
        for st in settings.storageList:
            conf = settings.storage_config.get(st)
            conf["filename"] = filename
            conf["packet_dir_path"] = response.get_packet_dir_path()
            self.upload_subpackage_dict.get(filename)[2].append(conf)

    def get_upload_task(self):
        while True:
            if len(self.upload_subpackage_dict) == 0:
                gevent.sleep(2)
            else:
                k, v = self.upload_subpackage_dict.popitem()
                if v[0] == 0:
                    # 全部上传成功，做一个通知 url = v[1]
                    logger.info("上传成功,删除子包")
                    os.remove(k)
                    self.message.finish_message_notice(v[1])
                    continue
                else:
                    conf = v[2].pop()
                    v[0] -= 1
                    self.upload_subpackage_dict[k] = v
                    self.upload_cloud(conf)

    def get_cloud_file_path(self, conf):
        filename = conf.get("filename")
        # apk_base_path = os.path.basename(filename).split("_")[0]
        apk_base_path = conf.get("packet_dir_path")
        cloud_filename = os.path.join(conf.get("basedir", ""), apk_base_path, os.path.basename(filename))
        return cloud_filename

    def get_driver_hand_way(self, conf, upload_file):
        driver = conf.get("DRIVER")
        upload_module = __import__("UploadFile." + driver)
        up_driver = getattr(getattr(upload_module, driver), driver)
        h_driver = up_driver(conf)
        upload_file = getattr(h_driver, "upload_file")
        return upload_file

    def upload_cloud(self, conf):
        filename = conf.get("filename")
        cloud_filename = self.get_cloud_file_path(conf)
        logger.debug(cloud_filename)
        upload_file = self.get_driver_hand_way(conf, "upload_file")
        try:
            upload_file(cloud_filename, filename)
        except Exception, e:
            logger.error(e, filename, "失败重传--------")
            # 将文件名封装进这个字典
            self.upload_subpackage_dict.get(filename)[0] += 1
            self.upload_subpackage_dict.get(filename)[2].append(conf)