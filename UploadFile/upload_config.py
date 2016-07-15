# coding:utf-8

# 设置云服务器类型 ks or oss及其基本配置
# storageList = ['oss1', 'ks1']
storageList = ['oss1']

storage_config = {
    "ks1": {
        "DRIVER": 'KSUpload',
        "AccessKey": 'gmvu0UYj0kwrTOoIIrcp',
        "SecretKey": '+pekrcxq1qR+oZ69Zahp6+gzYREDuT0TBEeSsy9e',
        "bucketName": 'sh-osstest',
        "ENDPOINT": 'ks3-cn-shanghai-internal.ksyun.com',
        "file_chunk_size": 20*1024*1024,
        "file_critical_size": 50*1024*1024,
        "basedir": "sdkgame",
    },
    "oss1": {
        "DRIVER": 'OSSUpload',
        "DOMAIN": "http://downapk.6y.com.cn/",
        "ACCESS_ID": "VPaDmdb3VoNB0k6t",
        "ACCESS_KEY": "jY1CoUcoKamDbaZZUIENIsRjfpTNCI",
        "ENDPOINT": "oss-cn-hangzhou-internal.aliyuncs.com",
        "BUCKET": "moge666",
        "file_chunk_size": 20*1024*1024,
        "file_critical_size": 50*1024*1024,
        "basedir": "sdkgame",
    },
}
