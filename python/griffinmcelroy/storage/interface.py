__author__ = 'achmed'

from abc import ABCMeta, abstractmethod


class SampleStorageInterface(object):
    '''
    a simple interface for storing samples
    '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def initialize(self, storagecfg):
        '''
        :param storagecfg: a config object which contains all storage directives.  the plugin will
        extract its own storage at a key known to it (i.e. webhdfs, postgres)
        :return: None
        '''
        pass

    @abstractmethod
    def persist_samples(self, samples):
        '''
        :param samples: a sequence of samples for persisting
        :return: None
        '''
        pass

    @abstractmethod
    def flush(self):
        '''
        if applicable, flush storage samples to backend immediately
        :return: None
        '''
        pass
