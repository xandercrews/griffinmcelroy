__author__ = 'achmed'

import time
import random
import string

from ...config.configwrapper import ConfigWrapper
from . import Gatherer
from ...scheduler import SkewlessScheduler
from ...sample import GriffinSample


import zmq
ctxt = zmq.Context(3)


import logging
logger = logging.getLogger(__name__)


class ZMQGatherer(object):
    def __init__(self, gathercfg, brokercfg):
        self.gathercfg = ConfigWrapper(other=gathercfg)
        self.brokercfg = ConfigWrapper(other=brokercfg)

        self.interval = self.gathercfg.getByPath('standalone.interval', 60.0)
        self.gatherer = Gatherer(self.gathercfg)

        self.sampletopic = self.gathercfg.getByPath('zmq.sampletopic', 'samples')

        self.pubaddr = self.gathercfg.getByPath('zmq.pubaddr', '127.0.0.1')
        self.pulladdr = self.gathercfg.getByPath('zmq.pulladdr', '127.0.0.1')
        self.pubport = self.brokercfg.getByPath('zmq.pubport', 59001)
        self.pullport = self.brokercfg.getByPath('zmq.pullport', 59000)

    def initialize(self):
        self.pushsocket = ctxt.socket(zmq.PUSH)
        self.pushsocket.connect('tcp://%s:%d' % (self.pulladdr, self.pullport))

        logger.info('initiated connection to broker@%s:%d' % (self.pulladdr, self.pullport))

        self.sync_pubsub()

    def mainloop(self):
        sched = SkewlessScheduler(self.interval)

        logger.info('starting poll loop')
        try:
            for ts in sched.schedule_generator():
                logger.info('starting poll')
                try:
                    for sampleset in self.gatherer.do_poll():
                        parts = map(GriffinSample.to_json, sampleset)
                        parts.insert(0, self.sampletopic)
                        self.pushsocket.send_multipart(parts, copy=False)
                except:
                    logger.exception('problem gathering and sending samples')
        except KeyboardInterrupt:
            logger.info('keyboard interrupt caught, stopping')

    def sync_pubsub(self, timeout=30):
        '''
        ensures the pubsub is receiving and transmitting the messages before continuing
        :return:
        '''
        now = time.time()
        timeout = now + timeout
        nonce = ''.join(random.sample(set(string.ascii_lowercase + string.ascii_uppercase + string.digits) - set([self.sampletopic[0]]), 20))
        assert nonce != self.sampletopic

        subsock = ctxt.socket(zmq.SUB)
        subsock.connect('tcp://%s:%d' % (self.pubaddr, self.pubport))
        logger.info('initiated sub connection for synchronization')
        subsock.setsockopt(zmq.SUBSCRIBE, nonce)
        subsock.setsockopt(zmq.SUBSCRIBE, 'samples')
        poller = zmq.Poller()
        poller.register(subsock, zmq.POLLIN)

        logger.info('starting poll, will sync or time out in %ds' % timeout)
        while now < timeout:
            now = time.time()

            # attempt to send nonce and receive it on the monitor port
            self.pushsocket.send_multipart([nonce])
            socks = poller.poll(50)
            if len(socks) > 0:
                msgparts = subsock.recv_multipart()
                assert msgparts[0] == nonce
                logger.info('synchronized with subscribe socket')
                subsock.disconnect('tcp://%s:%d' % (self.pubaddr, self.pubport))
                return

        raise Exception('timed out attempting to synchronize on sub socket')
