# coding:utf-8
import os
import time
import oss2
from baseUpload import BaseUpload
from UploadFile import upload_config
import logging
import logging.config
logging.config.fileConfig("logging.conf")
logger = logging.getLogger("")
class OSSUpload(BaseUpload):
    def __init__(self, oss_config):
        self.__access_id = oss_config.get("ACCESS_ID")
        self.__access_key = oss_config.get("ACCESS_KEY")
        self.__endpoint = oss_config.get("ENDPOINT")
        self.__bucket = oss_config.get("BUCKET")
        self.__file_chunk_size = oss_config.get("file_chunk_size")
        self.__file_critical_size = oss_config.get("file_critical_size")
        self.__parts = []

    def __connect_oss(self):
        auth = oss2.Auth(self.__access_id, self.__access_key)
        bucket = oss2.Bucket(auth, 'http://%s' % self.__endpoint, self.__bucket)
        return bucket

    def upload_file(self, cloud_file, file_to_upload):
        file_size = os.path.getsize(file_to_upload)
        if file_size > self.__file_critical_size:
            self.upload_chunk_file(cloud_file, file_to_upload)
            return
        bucket = self.__connect_oss()
        logger.debug("开始上传%s到OSS中" % file_to_upload)
        startTime = time.time()
        bucket.put_object_from_file(cloud_file, file_to_upload)
        endTime = time.time()
        spendTime = endTime - startTime
        logger.debug("上传%s完成" % file_to_upload)
        logger.debug("Upload file spent %f second." % (spendTime))

    def resumable(self, cloud_file, file_to_upload):
        logger.debug("开始断点续传%s" % (file_to_upload))
        startTime = time.time()
        bucket = self.__connect_oss()
        oss2.resumable_upload(bucket, cloud_file, file_to_upload,
                              store=oss2.ResumableStore(root='/tmp'),
                              multipart_threshold=self.__file_critical_size,
                              part_size=self.__file_chunk_size,
                              num_threads=10)
        endTime = time.time()
        spendTime = endTime - startTime
        logger.debug("Upload file spend %f second." % (spendTime))

    def upload_chunk_file(self, cloud_file, file_to_upload):
        bucket = self.__connect_oss()
        total_size = os.path.getsize(file_to_upload)
        part_size = oss2.determine_part_size(total_size, preferred_size=self.__file_chunk_size)
        file_part_count = (total_size / part_size) + 1
        upload_id = bucket.init_multipart_upload(cloud_file).upload_id
        parts = []
        logger.debug("开始分片存储%s " % file_to_upload )  # TODO 并发上传
        startTime = time.time()
        with open(file_to_upload, 'rb') as fileobj:
            part_number = 1
            offset = 0
            while offset < total_size:
                num_to_upload = min(part_size, total_size - offset)
                result = bucket.upload_part(cloud_file, upload_id, part_number,
                                            oss2.SizedFileAdapter(fileobj, num_to_upload))
                parts.append(oss2.models.PartInfo(part_number, result.etag))

                offset += num_to_upload
                part_number += 1
                logger.debug("upload chunk %d" % (part_number - 1) )

        bucket.complete_multipart_upload(cloud_file, upload_id, parts)
        endTime = time.time()
        spendTime = endTime - startTime
        logger.debug("Upload file spend %f second." % (spendTime))
