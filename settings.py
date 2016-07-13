#!/usr/bin/env python
# coding:utf-8
import logging
import os


# 主打包进程数
packet_num = 1
# 打包失败的尝试进程数
retry_packet_num =1
# 消息通知进程数
message_num = 1

# 上传失败的尝试进程数
retry_upload_num =1

# 消息存储方式
access = "redis"
# redis数据库的基本信息
redis_host = '121.199.34.235'
redis_port = 6379
redis_db = 0
redis_password = "uid"
redis_key = "6y:apk:subpackage:task"
redis_retry_key = "6y:apk:subpackage:retrytask"
redis_sleep_time = 10

#基本的打包状态消息
status_code = {

    #101 打包未进行
    'NO_READY' : {'statusCode': 101, 'message': "打包未开始"},

    # 201正常
    'COMPLETE' : {'statusCode': 201, 'message': "打包已完成"},

    #4XX 基本错误类型
    'ARG_MISS' : {'statusCode': 401, 'message':  "参数不完整，请检查"},
    'NO_APK': {'statusCode': 402, 'message': "游戏母包不存在"},
    'HAVEN_SUB': {'statusCode': 403, 'message': "游戏已分包，请勿重复操作"},
    'WRONG_APK': {'statusCode': 404, 'message': "apk文件不能正常读取"},
    'COPY_APK_ERROR': {'statusCode': 405, 'message': "无法创建文件,打包失败,请联系管理员"},
    'PERM_ERROR': {'statusCode': 406, 'message': "无法读取游戏母包, 请设置好访问权限"},

    # 5XX 特殊异常
    'UNKNOWN_ERROR': {'statusCode': 501, 'message': "UNKNOWN_ERROR"},

}

# 错误日志发送的平台
UDP_HOST = "218.85.13.145"
UDP_PORT = 1414

# 定义打包任务出错发送日志的时间
log_post_time = 30*60

# apk包的根路径
sdk_game_path = "apk"

# 分包时生成的临时文件路径
tempfile_dir = '/tmp'