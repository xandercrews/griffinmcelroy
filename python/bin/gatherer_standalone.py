__author__ = 'achmed'

import config

from griffinmcelroy.services.gatherer.standalone import StandloneGatherer
from griffinmcelroy.args import get_opts


import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('gatherer_standalone')
logger.setLevel(logging.DEBUG)


def main():
    opts = get_opts()

    c = config.Config(opts.config)
    if not hasattr(c, 'gatherer'):
        raise Exception('config is missing gatherer section')

    g = StandloneGatherer(c)
    g.mainloop()


if __name__ == '__main__':
    main()