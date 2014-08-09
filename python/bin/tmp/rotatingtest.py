__author__ = 'achmed'

import os

from griffinmcelroy.storage.webhdfs import RotatingSampleFile
from griffinmcelroy.iso8601 import get_iso8601_timestamp
from griffinmcelroy.sample import make_sample

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def did_rollback(oldfile):
    logger.info('called back with: ' + str(oldfile))

rsf = RotatingSampleFile(did_rollback, os.path.join('/tmp/', get_iso8601_timestamp() + '.json'), maxBytes=2048, backupCount=1)
for i in range(20):
    rsf.emit(make_sample('wat', 'wat', 'wat', 'wat', 'wat', {'wat': 'wat'}))
rsf.close()