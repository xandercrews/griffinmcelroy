__author__ = 'achmed'

import re

from ....sample import make_sample
from ..genericssh import GenericSSHGathererPlugin


import logging
logger = logging.getLogger(__name__)


madstat_p_split = re.compile(':\.\.+')


class ISR9024GathererPlugin(GenericSSHGathererPlugin):

    def initialize(self, name, plugincfg, devicecfg):
        super(ISR9024GathererPlugin, self).initialize(name, plugincfg, devicecfg)
        self.vendor = 'Voltaire'
        self.enablepass = self.devicecfg.get('enablepass', 'voltaire')
        self.lid = self.devicecfg.get('lid', 1)

    def get_samples(self):
        with self.ssh_connection() as cmd:
            cmd('enable')
            cmd(self.enablepass)
            cmd('utilities')
            ports = {}
            for port in xrange(1, 255):
                resp = cmd('madstat P %d %d'% (self.lid, port))
                if not '..........' in resp[0]:
                    break
                ports[port] = {}
                for line in resp[0:-1]:
                    field, val = madstat_p_split.split(line)
                    ports[port][field] = val

            numports = max(*ports.keys())
            freeports = len(filter(lambda d: d.get('physstate') != 'LinkUp', ports.values()))

        return [make_sample(self.site, self.deployment, self.vendor, 'isr9024', self.name, {
            'ports': {
                'total': numports,
                'free': freeports,
            }
        })]
