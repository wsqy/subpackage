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
    status = 1
    log_path = "log/del.log"
    task_subpackage_set = settings.task_subpackage_set + ":" + getMyIP.get_intranet_ip()
    rad_num = task.get_task_hand_way("random_member")
    rem_set = task.get_task_hand_way("rem_set")
    try:
        rad_num = rad_num(task_subpackage_set)
        if rad_num:
            os.remove(rad_num)
            status = 0
            rem_set(task_subpackage_set, rad_num)
            with open(log_path, "a+") as f:
                f.write("remove apk : %s\n" % rad_num)
    except Exception as e:
        with open(log_path, "a+") as f:
            f.write("%s\t, sleep %s s\n" % (e, settings.sleep_time))
        time.sleep(settings.sleep_time)
    finally:
        return status

if __name__ == "__main__":
    while True:
        status = remove_sub()
        if status:
            time.sleep(settings.sleep_time)


