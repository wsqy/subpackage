# coding:utf-8
from abc import ABCMeta, abstractmethod


class baseObj(object):
    __metaclass__ = ABCMeta

    def __init__(self, configuration):
        self.config = configuration

    @abstractmethod
    def get_task(self, key):
         pass

    def push_task(self, key, data):
        pass