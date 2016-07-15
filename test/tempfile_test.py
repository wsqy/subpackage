# encoding:utf-8
import settingqy


class Response:
    def __init__(self):
        self.status = False
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

    def get_status_code(self):
        return settingqy.status_code.get(self.status_key).get("statusCode")

    def get_message(self):
        return settingqy.status_code.get(self.status_key).get("message")

    def get_filename(self):
        return self.filename
