import apk
import time


def get_version_name(apk_name="../test.apk"):
    info = apk.APK(apk_name)
    print info.get_package()
    print info.get_androidversion_name()

if __name__ == "__main__":
    startTime = time.time()
    get_version_name()
    endTime = time.time()
    spendTime = endTime - startTime
    print "totally spent %f second" % spendTime