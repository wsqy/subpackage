# coding:utf-8
import os
import time
from gevent.monkey import patch_all
patch_all()
from gevent.pool import Pool
from ks3.connection import Connection
from filechunkio import FileChunkIO
from baseUpload import BaseUpload
import settings
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('mylogger')

class KSUpload(BaseUpload):
    def __init__(self, oss_config):
        self.__access_key = oss_config.get("AccessKey")
        self.__secret_key = oss_config.get("SecretKey")
        self.__endpoint = oss_config.get("ENDPOINT")
        self.__bucket = oss_config.get("bucketName")
        self.__file_chunk_size = oss_config.get("file_chunk_size")
        self.__file_critical_size = oss_config.get("file_critical_size")

    # 考虑到要实现分块上传，所以连接单独配置下
    def __connect_ks(self):
        ksConnect = Connection(self.__access_key, self.__secret_key, host=self.__endpoint)
        bucket = ksConnect.get_bucket(self.__bucket)
        return bucket

    def upload_file(self, cloud_file, file_to_upload):
        file_size = os.path.getsize(file_to_upload)
        startTime = time.time()
        if file_size > self.__file_critical_size:
            self.upload_chunk_file(cloud_file, file_to_upload)
            return
        bucket = self.__connect_ks()
        logger.info("开始上传%s。。。。到KS中" % file_to_upload)
        key_name = bucket.new_key(cloud_file)
        key_name.set_contents_from_filename(file_to_upload)
        endTime = time.time()
        spendTime = endTime - startTime
        logger.info("Upload file %s spent %f second." % (file_to_upload, spendTime))

    def upload_to_cloud(self, filePartInfo):
        startTime = time.time()
        filePartInfo['hMultiUpload'].upload_part_from_file(filePartInfo['fp'], filePartInfo['partIdx'])
        if not filePartInfo['fp'].closed:
            filePartInfo['fp'].close()
        endTime = time.time()
        spendTime = endTime - startTime
        logger.debug("Upload file part %d spent %f second." % (filePartInfo['partIdx'], spendTime))

    def upload_chunk_file(self, cloud_file, file_to_upload):
        bucket = self.__connect_ks()
        file_size = os.path.getsize(file_to_upload)

        if file_size < self.__file_critical_size:
            self.upload_file(cloud_file, file_to_upload)
            return
        file_part_count = (file_size / self.__file_chunk_size)+1
        startTime = time.time()
        file_parts = []
        h_multi_upload = bucket.initiate_multipart_upload(cloud_file)
        for chunkIdx in xrange(file_part_count):
            offset = self.__file_chunk_size * chunkIdx
            bytes = min(self.__file_chunk_size, file_size - offset)
            fp = FileChunkIO(file_to_upload, 'r', offset=offset, bytes=bytes)
            file_parts.append(dict(
                hMultiUpload=h_multi_upload,
                fp=fp,
                partIdx=chunkIdx + 1
            ))

        hPool = Pool(file_part_count)
        hPool.map(self.upload_to_cloud, file_parts)
        h_multi_upload.complete_upload()
        bucket.set_acl("public-read", cloud_file)
        endTime = time.time()
        spendTime = endTime - startTime
        logger.info("Upload file %s spent %f second." % (file_to_upload, spendTime))