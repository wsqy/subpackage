# coding:utf-8
import os
import time
import oss2
from gevent.monkey import patch_all
patch_all()
import gevent
import settings
from filechunkio import FileChunkIO
from baseUpload import BaseUpload
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('mylogger')


class OSSUpload(BaseUpload):
    def __init__(self, oss_config):
        self.__access_id = oss_config.get("ACCESS_ID")
        self.__access_key = oss_config.get("ACCESS_KEY")
        self.__endpoint = oss_config.get("ENDPOINT")
        self.__bucket = oss_config.get("BUCKET")
        self.__file_chunk_size = oss_config.get("file_chunk_size")
        self.__file_critical_size = oss_config.get("file_critical_size")
        self.muti_upload_chunk_num = 10
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
        logger.info("开始上传%s到OSS中" % file_to_upload)
        startTime = time.time()
        bucket.put_object_from_file(cloud_file, file_to_upload)
        endTime = time.time()
        spendTime = endTime - startTime
        logger.info("Upload file %s spent %f second." % (file_to_upload, spendTime))

    def resumable(self, cloud_file, file_to_upload):
        logger.info("开始断点续传%s" % (file_to_upload))
        startTime = time.time()
        bucket = self.__connect_oss()
        oss2.resumable_upload(bucket, cloud_file, file_to_upload,
                              store=oss2.ResumableStore(root='/tmp'),
                              multipart_threshold=self.__file_critical_size,
                              part_size=self.__file_chunk_size,
                              num_threads=10)
        endTime = time.time()
        spendTime = endTime - startTime
        logger.info("Upload file %s spent %f second." % (file_to_upload, spendTime))

    def complicate_upload(self, chunk_information):
        startTime = time.time()
        while len(chunk_information) > 0:
            chunk_info = chunk_information.pop(0)
            result = chunk_info["bucket"].upload_part(chunk_info["cloud_file"], chunk_info["upload_id"],
                                                      chunk_info["part_number"], chunk_info["file_size_adapter"])
            self.__parts.append(oss2.models.PartInfo(chunk_info["part_number"], result.etag))
            endTime = time.time()
            spendTime = endTime - startTime
            logger.debug("Upload file part %d of %s spent %f second." %
                         (chunk_info["part_number"], chunk_info["cloud_file"], spendTime))


    def upload_chunk_file(self, cloud_file, file_to_upload):
        bucket = self.__connect_oss()
        total_size = os.path.getsize(file_to_upload)
        part_size = oss2.determine_part_size(total_size, preferred_size=self.__file_chunk_size)
        file_part_count = (total_size / part_size) + 1
        upload_id = bucket.init_multipart_upload(cloud_file).upload_id
        chunk_information = []
        logger.info("开始分片存储%s " % file_to_upload )  # TODO 并发上传
        startTime = time.time()
        for chunkIdx in xrange(file_part_count):
            offset = part_size * chunkIdx
            bytes = min(part_size, total_size - offset)
            fp = FileChunkIO(file_to_upload, 'r', offset=offset, bytes=bytes)
            chunk_information.append(dict(
                bucket=bucket,
                cloud_file=cloud_file,
                upload_id=upload_id,
                part_number=chunkIdx+1,
                file_size_adapter=fp,
            ))
        muti_upload = []
        for each in range(self.muti_upload_chunk_num):
            muti_upload.append(gevent.spawn(self.complicate_upload, chunk_information))
        gevent.joinall(muti_upload)
        bucket.complete_multipart_upload(cloud_file, upload_id, self.__parts)
        endTime = time.time()
        spendTime = endTime - startTime
        logger.info("Upload file %s spent %f second." % (file_to_upload, spendTime))
