__author__ = 'achmed'

from abc import abstractmethod, ABCMeta

class GathererPluginInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def initialize(self, name, plugincfg, devconfig):
        """
        :param plugincfg: should be a python-config object which the plugin can use to get its configuration data
        :param connstring: should be the
        :return: None
        """
        pass

    @abstractmethod
    def get_samples(self):
        """
        :return: a sequence of json samples
        """
        pass