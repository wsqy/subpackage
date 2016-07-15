"""
uploaderList = {}

name = ['oss', 'ks']

for uploaderName in name:
	uploaderList[uploaderName] = __import__(uploaderName)
	
currentUploader = 'oss'
uploaderList[currentUploader].upload(xx,xxx);

"""
from UploadFile import upload_config

for st in upload_config.storageList: 
    conf = upload_config.storage_config.get(st)
    print conf
    hDriver = 'oss'
    currentUploader =
    conf.get("DRIVER")
    hDriver = currentUploader(conf)
    print(hDriver)
    # hDriver.upload_file(os.path.basename(filename), filename)