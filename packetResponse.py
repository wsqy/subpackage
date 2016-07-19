# encoding:utf-8
import settings


class Response:
    def __init__(self):
        self.status = False
        self.status_key = "NO_READY"
        self.error_code = "101"
        self.status_message = "打包未开始"
        self.packet_dir_path = None
        self.filename = None

    def set_status(self, status):
        self.status = status

    def set_status_key(self, status_key):
        self.status_key = status_key

    def set_message(self, message):
        self.status_message = message

    def set_filename(self, filename):
        self.filename = filename

    def set_packet_dir_path(self, path):
        self.packet_dir_path = path

    def get_status(self):
        return self.status

    def get_status_key(self):
        return self.status_key

    def get_error_code(self):
        return settings.packageInfo.get(self.status_key).get("errorCode")

    def get_message(self):
        return settings.packageInfo.get(self.status_key).get("message")

    def get_filename(self):
        return self.filename

    def get_packet_dir_path(self):
        return self.packet_dir_path

    def __unicode__(self):
        return self.get_status_key()