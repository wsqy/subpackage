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
import random
import settings
import sys


class Response:
    def __init__(self):
        self.status = True
        self.status_key = "NO_READY"
        self.status_code = "101"
        self.status_message = "打包未开始"
        self.filename = None

    def set_status(self, status):
        self.status = status

    def set_status_key(self, status_key):
        self.status_key = status_key

    def set_message(self,message):
        self.status_message = message

    def set_filename(self,filename):
        self.filename = filename

    def get_status(self):
        return self.status

    def get_status_key(self):
        return self.status_key

    def get_status_code(self):
        return settings.status_code.get(self.status_key).get("statusCode")

    def get_message(self):
        return settings.status_code.get(self.status_key).get("message")

    def get_filename(self):
        return self.filename

    def __unicode__(self):
        return self.get_status_key()

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
    return os.path.join(make_package_dir(filename), make_apk_file_name(filename, channel_id, version_name))


def zip_add_file(channel_file, target_file, date=None):
    # 获得临时文件目录
    tempfile_dir = settings.tempfile_dir

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
    time_file = os.path.join(meta_info_dir,str(int(time.time())))

    # 强更版本信息
    channel_version = str(extend.get("channel_version", 13))
    channel_version_file = os.path.join(meta_info_dir, 'mg_channel_version_%s' % channel_version)

    startTime = time.time()

    # 添加文件到压缩包
    data = {'author': 'admin'}
    zip_add_file(channel_file, channel_info_file, date=json.dumps(data))
    zip_add_file(channel_file, time_file, date=str(int(time.time())))
    zip_add_file(channel_file, channel_version_file, date=channel_version)

    endTime = time.time()
    spendTime = endTime - startTime
    # print "totally spent %f second" % spendTime


def subpackage(filename=None, channel_id=None, extend=None):
    response = Response()
    # 确认参数完整性
    if not filename or not channel_id:
        response.set_status(False)
        response.set_status_key('ARG_MISS')


    # 检查游戏母包是否存在
    source_file =''
    if response.get_status():
        source_file = make_parent_package_file(filename)
        if not os.path.exists(source_file):
            response.set_status(False)
            response.set_status_key('NO_APK')

    # 检查游戏母包权限
    if response.get_status():
        if not os.access(source_file, os.R_OK):
            response.set_status(False)
            response.set_status_key('PERM_ERROR')

    # 生成channel_file文件名并检查是否存在
    channel_file = ''
    if response.get_status():
        try:
            version_name = get_apk_version(source_file)
            channel_file = make_sub_package_file(filename, channel_id, version_name)
            if os.path.exists(channel_file):
                response.set_status(False)
                response.set_status_key('HAVEN_SUB')
        except IOError, e:
            response.set_status(False)
            response.set_status_key('WRONG_APK')
            response.set_message(e)
            return response

    # 复制母包文件
    if response.get_status():
        if not copyfile(source_file, channel_file):
            my_chmod(channel_file)
        else:
            response.set_status(False)
            response.set_status_key('COPY_APK_ERROR')

    # 开始分包
    if response.get_status():
        try :
            unpack(channel_file, channel_id, extend, version_name)
        except IOError, e:
            response.set_status(False)
            response.set_status_key('UNKNOWN_ERROR')
            response.set_special_message(e)
            return response


    if response.get_status():
        response.set_status_key("COMPLETE")
        response.set_filename(channel_file)
        '''
        这里需要把成功的分包信息写入日志
        '''
    else:
        # os.remove(channel_file)
        '''
        错误的扔进redis,并检测是否有消息超时时间，如果没有则添加此时间为当前时间的后 log_post_time 秒
        '''
    return response


if __name__ == "__main__":
    filename = "testapk"
    channel_id = 13
    extend = {"channel_version": "13"}
    startTime = time.time()
    response = subpackage(filename, channel_id, extend)
    endTime = time.time()
    spendTime = endTime - startTime
    print response.get_message()
    print "totally spent %f second" % spendTime