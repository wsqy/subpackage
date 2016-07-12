import os
import gevent

from UploadFile.KSUpload import KSUpload
from UploadFile.OSSUpload import OSSUpload
from UploadFile import upload_config


class upload:
    def __init__(self, upload_subpackage_dict, notice_url):
        self.upload_subpackage_dict = upload_subpackage_dict
        self.notice_url = notice_url

    def get_upload_info(self, filename):
        self.upload_subpackage_dict[filename] = [len(upload_config.storageList), []]
        while len(upload_config.storageList) != 0:
            st = upload_config.storageList.pop()
            conf = upload_config.storage_config.get(st)
            conf["filename"] = filename
            conf["notice_url"] = self.notice_url
            self.upload_subpackage_dict.get(filename)[1].append(conf)

    def upload_cloud(self, conf):
        h_driver = "oss"
        filename = conf.get("filename")
        print filename
        cloud_filename = os.path.join(conf.get("basedir", ""), os.path.basename(filename))
        if conf.get("DRIVER") == "ks":
            h_driver = KSUpload(conf)
        else:
            h_driver = OSSUpload(conf)
        try:
            h_driver.upload_file(cloud_filename, filename)
        except Exception, e:
            print e, filename, "失败重传--------"
            # 将文件名封装进这个字典
            self.upload_subpackage_dict.get(filename)[0] += 1
            self.upload_subpackage_dict.get(filename)[1].append(conf)

