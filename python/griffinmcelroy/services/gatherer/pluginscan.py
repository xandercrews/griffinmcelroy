__author__ = 'achmed'

import pkg_resources
import logging
logger = logging.getLogger(__name__)


def scan_gatherer_plugins():
    plugins = {}

    for ep in pkg_resources.iter_entry_points(group='griffinmcelroy.gatherers'):
        if ep.name not in plugins:
            plugins[ep.name] = ep
        else:
            previous_ep = plugins[ep.name]
            previous_dist = '%s:%s' % (previous_ep.dist.project_name, str(previous_ep.dist.version))
            this_dist = '%s:%s' % (ep.dist.project_name, str(ep.dist.version))
            logger.warn('plugin from %s already loaded for name %s, ignoring %s' % (previous_dist, ep.name, this_dist))

    return plugins

if __name__ == '__main__':
    scan_gatherer_plugins()