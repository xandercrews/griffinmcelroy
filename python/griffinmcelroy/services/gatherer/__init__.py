__author__ = 'achmed'

from .pluginscan import scan_gatherer_plugins
from ...gatherer.interface import GathererPluginInterface

import logging
logger = logging.getLogger(__name__)


class Gatherer(object):
    def __init__(self, cfg):
        self.cfgdevices = cfg.get('devices', {})
        self.cfgplugins = cfg.get('plugins', {})
        self.validate_config()
        self.load_all_plugins()
        self.initialize_all_devices()

    def validate_config(self):
        if len(self.cfgdevices) == 0:
            raise Exception('no devices configured')

        for devicename, device in self.cfgdevices.iteritems():
            if not hasattr(device, 'type'):
                raise Exception('missing device type for %s' % devicename)
            if not hasattr(device, 'connstring') and not device.get('docker', False):
                raise Exception('missing connection string for %s (and docker not enabled)' % devicename)

    def load_all_plugins(self):
        self.all_types = set(filter(None, [v.get('type', None) for d,v in self.cfgdevices.iteritems()]))
        self.all_plugins = scan_gatherer_plugins()

        self.plugins = {}

        for type in self.all_types:
            if type not in self.all_plugins:
                raise Exception('no plugin found to handle type %s' % type)
            assert type not in self.plugins
            ep = self.all_plugins[type]
            self.plugins[type] = ep.load()
            logger.info('loaded plugin %s for type %s' % (ep.name, type))

    def initialize_all_devices(self):
        self.devices = {}

        for name, deviceconfig in self.cfgdevices.iteritems():
            ptype = deviceconfig['type']
            dplugin = self.plugins[ptype]

            self.devices[name] = dplugin()
            self.devices[name] = dev = dplugin()

            if not isinstance(dev, GathererPluginInterface):
                raise Exception('device \'s\' is not a subclass of the gatherer plugin interface' % name)

            plugincfg = self.cfgplugins.get(ptype, {})

            dev.initialize(name, plugincfg, deviceconfig)

    def do_poll(self):
        for dname, d in self.devices.iteritems():
            assert isinstance(d, GathererPluginInterface)
            samples = d.get_samples()
            logger.info('got %d samples from %s' % (len(samples), dname))
            yield d.get_samples()
