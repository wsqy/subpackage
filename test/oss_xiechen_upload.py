def upload_to_cloud(self, filePartInfo):
        startTime = time.time()
        bucket = self.__connect_oss()
        result = filePartInfo['bucket'].upload_part(filePartInfo['key'], filePartInfo['upload_id'],filePartInfo['fp'])
        if not filePartInfo['fp'].closed:
            self.__parts.append(oss2.models.PartInfo(filePartInfo['partIdx'], result.etag))
            filePartInfo['fp'].close()
        endTime = time.time()
        spendTime = endTime - startTime
        print "Upload file part %d spent %f second." % (filePartInfo['partIdx'], spendTime)

    def upload_chunk_file(self, cloud_file, file_to_upload):
        bucket = self.__connect_oss()
        total_size = os.path.getsize(file_to_upload)
        part_size = oss2.determine_part_size(total_size, preferred_size=2*1024 * 1024)
        file_part_count = (total_size / part_size) + 1
        # ≥ı ºªØ∑÷∆¨
        upload_id = bucket.init_multipart_upload(cloud_file).upload_id
        file_parts = []
        startTime = time.time()
        for chunkIdx in xrange(file_part_count):
            offset = part_size * chunkIdx
            bytes = min(part_size, total_size - offset)
            fp = FileChunkIO(file_to_upload, 'r', offset=offset, bytes=bytes)
            file_parts.append(dict(
                bucket = bucket,
                key = cloud_file,
                hMultiUpload=upload_id,
                fp=fp,
                partIdx=chunkIdx + 1,
            ))
        hPool = Pool(file_part_count)
        hPool.map(self.upload_to_cloud, file_parts)
        bucket.complete_multipart_upload(cloud_file, upload_id, self.__parts)
        endTime = time.time()
        spendTime = endTime - startTime
        print "File %s size %d Byte" % (cloud_file, total_size)
        print "Upload file totally spent %f second" % spendTime