if __name__ == "__main__":
    filename = "/home/qy/packet/2/2.apk"
    for st in upload_config.storageList:
        try:
            conf = upload_config.storage_config.get(st)
            print conf
            hDriver = 'oss'
            if conf.get("DRIVER") == "ks":
                hDriver = KSUpload(conf)
            else:
                hDriver = OSSUpload(conf)
            hDriver.upload_file(os.path.basename(filename), filename)
        except Exception, e:
            print e