__author__ = 'achmed'

import config

from griffinmcelroy.services.gatherer.gatherer_zmq import ZMQGatherer
from griffinmcelroy.args import get_opts


import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('gatherer_zmq')
logger.setLevel(logging.DEBUG)


def main():
    opts = get_opts()

    c = config.Config(opts.config)
    if not hasattr(c, 'broker'):
        raise Exception('config is missing broker section')

    if not hasattr(c, 'gatherer'):
        raise Exception('config is missing gatherer section')

    b = ZMQGatherer(c.gatherer, c.broker)
    b.initialize()
    b.mainloop()


if __name__ == '__main__':
    main()
