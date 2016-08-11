#!/bin/env python2.7
# coding:utf-8

import os
import gevent
import settings
import task
from messageNotice import Message
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('mylogger')

upload_subpackage_dict = {}


class Upload:
    def __init__(self):
        self.no_task_sleep_time = settings.no_task_sleep_time

    def initialize_message(self):
        message = Message()
        return message

    def get_upload_info(self, response):
        filename = response["filename"]
        upload_subpackage_dict[filename] = [len(settings.storageList), response, []]
        for st in settings.storageList:
            conf = settings.storage_config.get(st)
            conf["filename"] = filename
            conf["packet_dir_path"] = response["packet_dir_path"]
            upload_subpackage_dict.get(filename)[2].append(conf)

    def get_upload_task(self):
        while True:
            if len(upload_subpackage_dict) == 0:
                gevent.sleep(self.no_task_sleep_time)
            else:
                filename, filename_config = upload_subpackage_dict.popitem()
                if filename_config[0] <= 0:
                    # 全部上传成功，做一个通知 url = filename_config[1]
                    # 从任务记录中删除待上传记录
                    delete_task = task.get_task_hand_way("delete_task")
                    delete_task(settings.upload_file_schedule_key, filename_config[1])
                    # 上传成功 从唯一性任务集合中删除
                    rem_set = task.get_task_hand_way("rem_set")
                    rem_set(settings.task_execute_key, filename)

                    base_dir = os.path.split(os.path.realpath(__file__))[0]
                    file_path = os.path.join(base_dir, filename)
                    logger.debug("子包全路径为:%s" % file_path)
                    add_set = task.get_task_hand_way("add_set")
                    add_set(settings.task_subpackage_set, file_path)
                    logger.debug("塞子包%s完成" % file_path)

                    message = self.initialize_message()
                    logger.debug("上传完成，准备通知%s" % (filename_config[1]["notice_url"]))
                    message.finish_message_notice(filename_config[1]["notice_url"])

                elif len(filename_config[2]) == 0:
                    upload_subpackage_dict[filename] = filename_config
                    gevent.sleep(self.no_task_sleep_time)
                else:
                    conf = filename_config[2].pop()
                    # self.upload_cloud(conf)
                    # v[0] -= 1
                    upload_subpackage_dict[filename] = filename_config
                    self.upload_cloud(conf)

    def get_cloud_file_path(self, conf):
        filename = conf.get("filename")
        # apk_base_path = os.path.basename(filename).split("_")[0]
        apk_base_path = conf.get("packet_dir_path")
        cloud_filename = os.path.join(conf.get("basedir", ""), apk_base_path, os.path.basename(filename))
        return cloud_filename

    def get_driver_hand_way(self, conf):
        driver = conf.get("DRIVER")
        upload_module = __import__("UploadFile." + driver, globals(), locals(), [driver])
        h_driver = getattr(upload_module, driver)
        h_driver = h_driver(conf)
        upload_file = getattr(h_driver, "upload_file")
        return upload_file

    def upload_cloud(self, conf):
        filename = conf.get("filename")
        cloud_filename = self.get_cloud_file_path(conf)
        logger.debug(cloud_filename)
        upload_file = self.get_driver_hand_way(conf)
        try:
            has_subfile = os.path.isfile(filename)
            if has_subfile:
                upload_file(cloud_filename, filename)
                upload_subpackage_dict.get(filename)[0] -= 1
            else:
                logger.error("子包%s路径不存在....." % filename)
        except Exception, e:
            logger.error(e)
            # 将文件名封装进这个字典
            # upload_subpackage_dict.get(filename)[0] += 1
            upload_subpackage_dict.get(filename)[2].append(conf)
