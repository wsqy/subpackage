#!/usr/bin/env python2.7
# coding:utf-8
import os
import getMyIP
import time
import settings
import task


def del_remove(info):
    os.remove(info)


def del_system(info):
    os.system("rm -f %s" % info)


def remove_sub():
    log_path = "log/del.log"
    task_subpackage_set = settings.task_subpackage_set + ":" + getMyIP.get_intranet_ip()
    rad_num = task.get_task_hand_way("random_member")
    rem_set = task.get_task_hand_way("rem_set")
    try:
        rad_num = rad_num(task_subpackage_set)
        if rad_num:
            with open(log_path, "a+") as f:
                f.write("get apk : %s\n" % rad_num)
            os.remove(rad_num)
            rem_set(task_subpackage_set, rad_num)
    except TypeError as e:
        with open(log_path, "a+") as f:
            f.write("%s\t, sleep %s s....." % (e, settings.sleep_time))
        time.sleep(settings.sleep_time)

if __name__ == "__main__":
    while True:
        remove_sub()
        time.sleep(settings.sleep_time)


