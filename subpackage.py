#! /usr/bin/env python
# coding:utf-8
import signal
import time
import urllib2
import os
import socket
from gevent import monkey
monkey.patch_all()
import gevent

import settings
import packet

from PacketRequest.RedisObj import RedisObj
from UploadFile.KSUpload import KSUpload
from UploadFile.OSSUpload import OSSUpload
from UploadFile import upload_config
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


class SubPackage:
    def __init__(self):
        self.retry_packet_num = settings.retry_packet_num
        self.packet_num = settings.packet_num
        self.message_num = settings.message_num
        self.retry_upload_num = settings.retry_upload_num
        self.redis_sleep_time = settings.redis_sleep_time
        self.message_list = []
        self.upload_subpackage_dict = {}
        self.is_run = True
        self.log_post_time = settings.log_post_time
        self.__UDP_host = settings.UDP_HOST
        self.__UDP_port = settings.UDP_PORT 

    def setQuit(self, pid, signal_num):
        self.is_run = False

    def gevent_join(self):
        gevent_task = [] 
        for each in range(self.packet_num):
            gevent_task.append(gevent.spawn(self.packet)) 
        for each in range(self.retry_packet_num):
            gevent_task.append(gevent.spawn(self.retry_packet)) 
        for each in range(self.message_num):
            gevent_task.append(gevent.spawn(self.message_queue))
        for each in range(self.retry_upload_num):
            gevent_task.append(gevent.spawn(self.get_upload_task))
        gevent.joinall(gevent_task)

    def alarm_info_format(self, level, Info):
        return "%s\t%s\t%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), level, Info)

    def finish_message_notice(self, Info_url):
        print "任务完成。。。。"
        return
        try:
            response = urllib2.urlopen(Info_url).read()
            if "success" in response :
                # 打个成功的日志
                print "消息发送成功"
                print "上传成功删除文件"
            elif "miss" in response:
                self.sent_log_info(self.alarm_info_format("notice", "missing"))
                print "miss"
            else:
                self.message_list.append(Info_url)
                print "other"
        except:
            print "url不可达"
            self.message_list.append(Info_url)

    def message_queue(self):
        # 如果通知队列中有消息则发送消息
        if len(self.message_list) == 0:
            gevent.sleep(self.redis_sleep_time)
        else:
            post_data = self.message_list.pop()
            self.finish_message_notice(post_data)

    def sent_log_info(self, data):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPTarget = (self.__UDP_host, self.__UDP_port)
        print "发送日志"
        s.sendto(data, UDPTarget)
        s.close()

    def subpackage_upload_handle(self, response, data_loads):
        message = response.get_status_key()
        if message == "COMPLETE":
            filename = response.get_filename()
            finish_url = data_loads.get("finish_notice_url")
            print " 准备上传%s。。。。。。" % filename
            self.get_upload_info(filename, finish_url)
        else:
            # 错误的扔进redis, 并检测是否有消息超时时间，如果没有则添加此时间为当前时间的后log_post_time 秒
            if not data_loads.get("extend").get("packet_timeout", None):
                data_loads["extend"]["packet_timeout"] = time.time() + self.log_post_time
            data_loads["extend"]["error_key"] = message
            redis_object = RedisObj()
            redis_object.push_task(redis_object.redis_retry_key, data_loads)

    def get_upload_info(self, filename, notice_url):
        self.upload_subpackage_dict[filename] = [len(upload_config.storageList), notice_url, []]
        for st in upload_config.storageList:
            conf = upload_config.storage_config.get(st)
            conf["filename"] = filename
            self.upload_subpackage_dict.get(filename)[2].append(conf)

    def get_upload_task(self):
        while True:
            if len(self.upload_subpackage_dict) == 0:
                gevent.sleep(2)
            else:
                k, v = self.upload_subpackage_dict.popitem()
                if v[0] == 0:
                    # 全部上传成功，做一个通知 url = v[1]
                    print "上传成功,删除子包"
                    os.remove(k)
                    self.finish_message_notice(v[1])
                    continue
                else:
                    conf = v[2].pop()
                    v[0] -= 1
                    self.upload_subpackage_dict[k] = v
                    self.upload_cloud(conf)

    def upload_cloud(self, conf):
        h_driver = "oss"
        filename = conf.get("filename")
        # print filename
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
            self.upload_subpackage_dict.get(filename)[2].append(conf)

    def packet(self):
        while True:
            if not self.is_run:
                # self.sent_log_info(self.alarm_info_format("warning", "been kill"))
                break
            print "开始解任务。。。。。"
            # 获取消息的redis ,并解码成python格式
            redis_object = RedisObj()
            data_loads = redis_object.get_task(redis_object.redis_key)
            print "开始分包。。。。"
            startTime = time.time()
            response = packet.subpackage(filename=data_loads.get("filename"),
                                         channel_id=data_loads.get("channel_id"),
                                         extend=data_loads.get("extend"),
                                         )
            endTime = time.time()
            spendTime = endTime - startTime
            print "subpackage spent %f second." % spendTime
            self.subpackage_upload_handle(response, data_loads)

    def retry_packet(self):
        while True:
            if not self.is_run:
                # self.sent_log_info(self.alarm_info_format("warning", "been kill"))
                break
            # 获取消息的redis ,并解码成python格式
            redis_object = RedisObj()
            data_loads = redis_object.get_task(redis_object.redis_retry_key)
            # filename channel_id channel_version finish_notice_url 如果有
            # 检查是否有超时时间，是否超过半个小时
            error_time = data_loads.get("extend").get("packet_timeout", None)
            if (error_time) and time.time() > error_time:
                self.sent_log_info(self.alarm_info_format(
                    "error", data_loads.get("extend").get("error_key")))
            # subpackage(filename, channel_id, extend)
            response = packet.subpackage(filename=data_loads.get("filename"),
                                         channel_id=data_loads.get("channel_id"),
                                         extend=data_loads.get("extend"),
                                         )
            self.subpackage_upload_handle(response, data_loads)


if __name__ == "__main__":
    # with daemon.DaemonContext():
        p = SubPackage()
        signal.signal(signal.SIGHUP, p.setQuit)
        p.gevent_join()
