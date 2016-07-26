# coding:utf-8


from abc import ABCMeta, abstractmethod



class BaseUpload(object):
    __metaclass__ = ABCMeta

    def __init__(self, configuration):
        self.config = configuration

    @abstractmethod
    def upload_file(self, cloud_file, file_to_upload):
        # raise NotImplementedError
        pass