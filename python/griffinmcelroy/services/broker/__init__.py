__author__ = 'achmed'

import zmq
from zmq.devices import Device

from ...config.configwrapper import ConfigWrapper


import logging
logger = logging.getLogger(__name__)


class ZMQSampleBroker(object):
    def __init__(self, cfg):
        self.cfg = ConfigWrapper(other=cfg.get('zmq'))
        self.pulladdr = cfg.get('pulladdr', '0.0.0.0')
        self.pubaddr = cfg.get('pubaddr', '0.0.0.0')
        self.pullport = cfg.get('pullport', 59000)
        self.pubport = cfg.get('pubport', 59001)

    def initialize(self):
        self.forwarddevice = Device(zmq.QUEUE, zmq.PULL, zmq.PUB)
        self.forwarddevice.bind_in('tcp://%s:%d' % (self.pulladdr, self.pullport))
        self.forwarddevice.bind_out('tcp://%s:%d' % (self.pubaddr, self.pubport))
        logger.info('created broker in: PULL@%s:%d out: PUB@%s:%d' % (self.pulladdr, self.pullport, self.pubaddr, self.pubport))

    def start(self):
        logger.info('starting broker')
        self.forwarddevice.start()
