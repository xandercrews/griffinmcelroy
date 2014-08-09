__author__ = 'achmed'

import json
import time

from ...config.configwrapper import ConfigWrapper
from ...storage import storage_backend_config_loader
from ...sample import GriffinSample

import zmq
ctxt = zmq.Context(2)


import logging
logger = logging.getLogger(__name__)


class ZMQAggregator(object):
    def __init__(self, brokercfg, gatorcfg):
        self.brokercfg = ConfigWrapper(other=brokercfg)
        self.gatorcfg = ConfigWrapper(other=gatorcfg)

        self.pubaddr = self.gatorcfg.getByPath('zmq.pubaddr', '127.0.0.1')
        self.pubport = self.brokercfg.getByPath('zmq.pubport', 59000)
        self.sampletopic = self.gatorcfg.getByPath('zmq.sampletopic', 'samples')

        self.storageconfig = ConfigWrapper(other=self.gatorcfg.get('storage'))
        self.storage = storage_backend_config_loader(self.storageconfig)

    def initialize(self, ):
        self.subsock = ctxt.socket(zmq.SUB)
        self.subsock.setsockopt(zmq.SUBSCRIBE, self.sampletopic)
        self.subsock.connect('tcp://%s:%d' % (self.pubaddr, self.pubport))
        logger.info('initiated connection to tcp://%s:%d' % (self.pubaddr, self.pubport))

    def mainloop(self):
        logger.info('entering recv loop')
        while True:
            try:
                samples = self.subsock.recv_multipart(copy=False)
            except zmq.ZMQError, e:
                logger.exception('received zmq error')
                time.sleep(0.1)
                continue

            if samples[0].bytes != self.sampletopic:
                logger.warn('received non-topic as first message part')
                continue
            else:
                samples = samples[1:]
                sampleobs = []
                for sample in samples:
                    try:
                        sample = json.loads(sample.bytes)
                    except Exception, e:
                        logger.warn('received non-json sample')
                        continue

                    try:
                        sample = GriffinSample.from_dict(sample)
                    except Exception, e:
                        logger.warn('problem converting unmarshalling sample')
                        continue

                    sampleobs.append(sample)

            try:
                if len(sampleobs) > 0:
                    self.storage.persist_samples(sampleobs)
                    logger.info('persisted %d samples' % len(sampleobs))
            except:
                logger.exception('problem persisting samples')