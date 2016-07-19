#!/usr/bin/env python
# coding:utf-8
import os


# 主打包进程数
packet_num = 3
# 打包失败的尝试进程数
retry_packet_num = 3
# 消息通知进程数
message_num = 1

# 上传失败的尝试进程数
retry_upload_num =1

# 消息存储方式
task_type = "redis"
# redis数据库的基本信息
redis_host = '2cdd06c0eba54c30.m.cnhza.kvstore.aliyuncs.com'
redis_port = 6379
redis_db = 0
redis_auth = "nhuWq6vgsEypdZF"
task_store_key = "6y:apk:subpackage:task"
task_store_retry_key = "6y:apk:subpackage:retrytask"
no_task_sleep_time = 3

# 基本的打包状态消息
packageInfo = {

    #101 打包未进行
    'NO_READY' : {'errorCode': 101, 'message': "打包未开始"},

    # 201正常
    'COMPLETE' : {'errorCode': 201, 'message': "打包已完成"},

    #4XX 基本错误类型
    'ARG_MISS' : {'errorCode': 401, 'message':  "参数不完整，请检查"},
    'NO_APK': {'errorCode': 402, 'message': "游戏母包不存在"},
    'HAVEN_SUB': {'errorCode': 403, 'message': "游戏已分包，请勿重复操作"},
    'WRONG_APK': {'errorCode': 404, 'message': "apk文件不能正常读取"},
    'COPY_APK_ERROR': {'errorCode': 405, 'message': "无法创建文件,打包失败,请联系管理员"},
    'PERM_ERROR': {'errorCode': 406, 'message': "无法读取游戏母包, 请设置好访问权限"},

    # 5XX 特殊异常
    'UNKNOWN_ERROR': {'errorCode': 501, 'message': "UNKNOWN_ERROR"},

}

# 错误日志发送的平台
UDP_HOST = "218.85.13.145"
UDP_PORT = 1414

# 定义打包任务出错发送日志的时间
log_post_time = 30*60

# apk包的根路径
sdk_game_path = "/data/www/6y_download/sdkgame"

# 子包路径
subpackage_sdk_path = ''

# 分包时生成的临时文件路径
tempfile_dir = '/tmp'

# 生成随机字符串时，字符只能在下列字符串中
random_chr = 'abcdefghjkmnpqrstuvwxyz23456789QWERTYUIPASDFGHJKLMNBVCXZ'

debug = False


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


# 定义日志相关配置

# 日志文件夹的根目录
logging_directory_path = 'log'

# 日志配置文件
def logging_file_path(filename):
    return os.path.join(logging_directory_path, filename)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'notes': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logging_file_path('all.log'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'default',
        },
        'scripts': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logging_file_path('scripts.log'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'default',
        },
        'errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': logging_file_path('error.log'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'default',
        },
    },
    'loggers': {
        # 定义了一个logger
        'mylogger': {
            'level': 'DEBUG',
            'handlers': ['console', 'notes', 'scripts', 'errors'],
            'propagate': True
        }
    }
}
