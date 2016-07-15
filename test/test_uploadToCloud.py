# coding:utf-8

import os
import time
from abc import ABCMeta, abstractmethod

import oss2

from UploadFile import upload_config


class UploadToCloud(object):
    __metaclass__ = ABCMeta

    def __init__(self, configuration):
        self.config = configuration

    @abstractmethod
    def upload_file(self, file_to_upload, cloud_file):
        # raise NotImplementedError
        pass


class OSSUpload(UploadToCloud):
    def __init__(self, oss_config):
        self.__access_id = oss_config.get("ACCESS_ID")
        self.__access_key = oss_config.get("ACCESS_KEY")
        self.__endpoint = oss_config.get("ENDPOINT")
        self.__bucket = oss_config.get("BUCKET")

    def upload_file(self, file_to_upload, cloud_file):
        auth = oss2.Auth(self.__access_id, self.__access_key)
        bucket = oss2.Bucket(auth, 'http://%s' % self.__endpoint, self.__bucket)
        bucket.put_object_from_file(cloud_file, file_to_upload)


if __name__ == "__main__":
    filename = "2.apk"
    print os.path.exists(filename)
    for st in upload_config.storageList:
        try:
            conf = upload_config.storage_config.get(st)
            print conf
            hDriver = 'oss'
            hDriver = OSSUpload(conf)
            print hDriver
            print "starting......."
            startTime = time.time()
            hDriver.upload_file(filename, filename)
            endTime = time.time()
            spendTime = endTime - startTime
            print spendTime
        except Exception, e:
            print e
