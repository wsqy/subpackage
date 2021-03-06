#! /usr/bin/env python
# encoding:utf-8
import os
import json
import time
import subprocess
from shutil import copyfile
import zipfile
import tempfile
from AxmlParserPY import apk
import task
import settings
import random
import packetResponse
import logging.config
logging.config.dictConfig(settings.LOGGING)
logger = logging.getLogger('mylogger')


sdk_game_path = settings.sdk_game_path
if not sdk_game_path:
    sdk_game_path = os.getcwd()


def my_chmod(file_name, ch=777):
    cmd = 'chmod %s %s ' % (ch, file_name)
    if os.name == 'nt':
        subprocess.call(cmd, shell=True)


def make_package_dir(filename):
    return os.path.join(sdk_game_path, filename)


def make_parent_package_file(filename):
    return os.path.join(make_package_dir(filename), r'%s.apk' % filename)


def get_apk_version(apk_name):
    info = apk.APK(apk_name)
    version_name = info.get_androidversion_name()
    if not version_name:
        return '0'
    else:
        return version_name


def make_apk_file_name(filename, channel_id, version_name):
    return "%s_%s_%s.apk" % (filename, channel_id, version_name)


def make_sub_package_file(filename, channel_id, version_name):
    if settings.subpackage_sdk_path :
        if not os.path.isdir(settings.subpackage_sdk_path):
            os.mkdir(settings.subpackage_sdk_path)
        return os.path.join(settings.subpackage_sdk_path, make_apk_file_name(filename, channel_id, version_name))
    return os.path.join(make_package_dir(filename), make_apk_file_name(filename, channel_id, version_name))


def zip_add_file(channel_file, target_file, date=None):
    # 获得临时文件目录
    tempfile_dir = settings.tempfile_dir
    if not tempfile_dir:
        tempfile_dir = os.getcwd()

    # 添加文件到压缩包
    with zipfile.ZipFile(channel_file, 'a', zipfile.ZIP_DEFLATED) as zip_opt:
        with tempfile.NamedTemporaryFile(dir=tempfile_dir) as temp_file_opt:
            # print temp_file_opt.name
            time.sleep(5)
            temp_file_opt.write(date)
            temp_file_opt.seek(0)
            zip_opt.write(temp_file_opt.name, target_file)


def unpack(channel_file=None, channel_id=None, extend={}, version_name=None):
    meta_info_dir = 'META-INF'

    # 生成json文件
    json_file_name = r'gamechannel_%s_.json' % channel_id
    channel_info_file = os.path.join(meta_info_dir, json_file_name)

    # 以当前的时间戳为文件名，生成附件文件，避免apk传输过程中被缓存旧包
    random_str = str(time.time()) + "".join(
                 random.sample(settings.random_chr,
                 random.randint(1, len(settings.random_chr))))

    time_file = os.path.join(meta_info_dir, random_str)

    # 强更版本信息
    channel_version = str(extend.get("channel_version", 13))
    channel_version_file = os.path.join(meta_info_dir, 'mg_channel_version_%s' % channel_version)

    startTime = time.time()
    if not os.path.isfile(channel_file):
        logger.error("子包%s路径错误....." % (channel_file))
    # 添加文件到压缩包
    data = {'author': 'admin'}
    zip_add_file(channel_file, channel_info_file, date=json.dumps(data))
    zip_add_file(channel_file, time_file, date=random_str)
    zip_add_file(channel_file, channel_version_file, date=channel_version)

    endTime = time.time()
    spendTime = endTime - startTime
    # print "totally spent %f second" % spendTime


def subpackage(filename=None, channel_id=None, extend=None):
    response = packetResponse.Response()
    response.set_filename(filename)
    # 确认参数完整性
    if not filename or not channel_id:
        response.set_status_key('ARG_MISS')
        return response
    # 检查游戏母包是否存在
    source_file = make_parent_package_file(filename)
    if not os.path.exists(source_file):
        response.set_status_key('NO_APK')
        return response
    # 检查游戏母包权限
    if not os.access(source_file, os.R_OK):
        response.set_status_key('PERM_ERROR')
        return response
    # 生成channel_file文件名并检查是否存在
    channel_file = ''
    try:
        version_name = get_apk_version(source_file)
        channel_file = make_sub_package_file(filename, channel_id, version_name)
        add_set = task.get_task_hand_way("add_set")
        status = add_set(settings.task_execute_key, channel_file)
        if status == 0:
            response.set_status_key('execute')
            return response
        if "enforcement" not in extend:
            enforcement = True
        else:
            enforcement = extend.get("enforcement")
        logger.debug("母包%s是否需要强制分包:%s" % (filename, enforcement))
        if os.path.exists(channel_file):
            if not enforcement:
                response.set_status_key('HAVEN_SUB')
                response.set_filename(channel_file)
                response.set_packet_dir_path(filename)
                return response
            else:
                os.remove(channel_file)
    except Exception, e:
        response.set_status_key('WRONG_APK')
        logger.error(e)
        response.set_message(e)
        return response
    # 复制母包文件
    if not copyfile(source_file, channel_file):
        my_chmod(channel_file)
    else:
        response.set_status_key('COPY_APK_ERROR')
        return response
    # 开始分包
    try:
        unpack(channel_file, channel_id, extend, version_name)
    except Exception, e:
        response.set_status(False)
        response.set_status_key('UNKNOWN_ERROR')
        logger.error(e)
        response.set_message(e)
        return response
    response.set_status("True")
    response.set_status_key("COMPLETE")
    response.set_filename(channel_file)
    response.set_packet_dir_path(filename)
    return response


if __name__ == "__main__":
    filename = "1"
    channel_id = 13
    extend = {"channel_version": "13"}
    startTime = time.time()
    response = subpackage(filename, channel_id, extend)
    endTime = time.time()
    spendTime = endTime - startTime
    print response.get_message()
    print "totally spent %f second" % spendTime
