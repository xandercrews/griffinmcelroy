from ...config.configwrapper import ConfigWrapper
from . import Gatherer
from ...scheduler import SkewlessScheduler
from ...storage import storage_backend_config_loader

import logging
logger = logging.getLogger(__name__)


class StandloneGatherer(object):
    def __init__(self, cfg):
        self.gatherconfig = ConfigWrapper(other=cfg.get('gatherer'))
        self.interval = self.gatherconfig.getByPath('standalone.interval', 60.0)
        self.gatherer = Gatherer(self.gatherconfig)
        self.storageconfig = ConfigWrapper(other=self.gatherconfig.get('storage'))
        self.storage = storage_backend_config_loader(self.storageconfig)

    def mainloop(self):
        sched = SkewlessScheduler(self.interval)

        try:
            for ts in sched.schedule_generator():
                logger.info('starting poll')
                try:
                    for sampleset in self.gatherer.do_poll():
                        self.storage.persist_samples(sampleset)
                        logger.info('persisted %d samples' % len(sampleset))
                except:
                    logger.exception('problem gathering and persisting samples')
        except KeyboardInterrupt:
            logger.info('keyboard interrupt caught, stopping')
        finally:
            self.storage.flush()
