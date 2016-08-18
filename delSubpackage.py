#!/usr/bin/env python2.7
# coding:utf-8

import os
import getMyIP
import time
import settings
import task


def generate_log_filename(log_type):
    get_date = time.strftime("%m%d", time.localtime())
    log_filename = "%s%s.log" % (log_type, get_date)
    return os.path.join(settings.del_log_path, log_filename)


def chunk_filename(filename):
    """
    检查文件路径是否符合规则，检测到不符合的规则项，直接return 1
    """
    if len(filename) < 15:
        return "size of %s is %s, less than 15\n" % (filename, len(filename))
    file_path = os.path.abspath(filename)
    if file_path.startswith(settings.sdk_game_path):
        return 0
    else:
        return "error! %s not startswith %s\n" % (filename, settings.sdk_game_path)


def remove_sub():
    status = 1
    log_path = generate_log_filename("del")
    task_subpackage_set = settings.task_subpackage_set_prefix + ":" + getMyIP.get_intranet_ip()
    rad_num = task.get_task_hand_way("random_member")
    rem_set = task.get_task_hand_way("rem_set")
    try:
        rad_num = rad_num(task_subpackage_set)
        if rad_num:
            message = chunk_filename(rad_num)
            if message:
                with open(log_path, "a+") as f:
                    f.write(message)
                rem_set(task_subpackage_set, rad_num)
                return 0
            os.remove(rad_num)
            status = 0
            rem_set(task_subpackage_set, rad_num)
            with open(log_path, "a+") as f:
                f.write("remove apk : %s\n" % rad_num)
    except Exception as e:
        with open(log_path, "a+") as f:
            f.write("no data, sleep %s s\n" % settings.sleep_time)
    finally:
        return status

if __name__ == "__main__":
    settings.mkdir_log_path(settings.del_log_path)
    while True:
        status = remove_sub()
        if status:
            time.sleep(settings.sleep_time)


