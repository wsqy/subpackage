#!/usr/bin/env python2.7
# coding:utf-8
import os
import getMyIP
import time
import settings
import task


def remove_sub():
    task_subpackage_set = settings.task_subpackage_set + ":" + getMyIP.get_intranet_ip()
    rad_num = task.get_task_hand_way("random_member")
    rem_set = task.get_task_hand_way("rem_set")
    while True:
        try:
            rad_num = rad_num(task_subpackage_set)
            if not rad_num:
                print("no data,sleep %s s....." % settings.sleep_time)
                time.sleep(settings.sleep_time)
                continue
            print("get apk : %s" % rad_num)
            os.remove(rad_num)
            rem_set = rem_set(task_subpackage_set, rad_num)
        except TypeError as e:
            print("sleep %s s....." % settings.sleep_time)
            time.sleep(settings.sleep_time)
            continue

if __name__ == "__main__":
    remove_sub()


