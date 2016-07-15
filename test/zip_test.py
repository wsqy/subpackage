import zipfile
import time
import tempfile_test
import os
import json


def zipopt(channel_file, channel_id=13, extend={}):
    metaInfoDirPath = 'META-INF'
    jsonFileName = r'gamechannel_%s_.json' % channel_id
    channel_info_file = os.path.join(metaInfoDirPath, jsonFileName)
    time_file = os.path.join(metaInfoDirPath, str(int(time.time())))
    channel_version = str(extend.get("channel_version", 13))
    channel_version_file = os.path.join(metaInfoDirPath, 'mg_channel_version_%s' % channel_version)
    with zipfile.ZipFile(channel_file, 'a', zipfile.ZIP_DEFLATED) as zip_opt:
        #  channel_info_file
        with tempfile_test.NamedTemporaryFile() as temp_file_opt:
            data = {'author': 'admin'}
            temp_file_opt.write(json.dumps(data))
            temp_file_opt.seek(0)
            zip_opt.write(temp_file_opt.name, channel_info_file)
        # channel_info_file
        with tempfile_test.NamedTemporaryFile() as temp_file_opt:
            temp_file_opt.write(str(int(time.time())))
            temp_file_opt.seek(0)
            zip_opt.write(temp_file_opt.name, time_file)
        # channel_info_file
        with tempfile_test.NamedTemporaryFile() as temp_file_opt:
            channel_version = str(extend.get("channel_version", 13))
            temp_file_opt.write(channel_version)
            temp_file_opt.seek(0)
            zip_opt.write(temp_file_opt.name, channel_version_file)


if __name__ == "__main__":
    startTime = time.time()
    channel_file = "big.apk"
    zipopt(channel_file)
    endTime = time.time()
    spendTime = endTime - startTime
    print "totally spent %f second" % spendTime
