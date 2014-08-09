__author__ = 'achmed'

import config

from griffinmcelroy.services.gator.aggregator_zmq import ZMQAggregator
from griffinmcelroy.args import get_opts


import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('gator_zmq')
logger.setLevel(logging.DEBUG)


def main():
    opts = get_opts()

    c = config.Config(opts.config)
    if not hasattr(c, 'broker'):
        raise Exception('config is missing broker section')

    if not hasattr(c, 'gator'):
        raise Exception('config is missing gator section')

    b = ZMQAggregator(c.broker, c.gator)
    b.initialize()
    b.mainloop()


if __name__ == '__main__':
    main()
