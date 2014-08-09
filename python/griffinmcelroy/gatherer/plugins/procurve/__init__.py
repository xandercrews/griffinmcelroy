__author__ = 'achmed'

from ....sample import make_sample
from ..genericssh import GenericSSHGathererPlugin


import logging
logger = logging.getLogger(__name__)


class ProcurveGathererPlugin(GenericSSHGathererPlugin):

    def initialize(self, name, plugincfg, devicecfg):
        super(ProcurveGathererPlugin, self).initialize(name, plugincfg, devicecfg)
        self.vendor = 'HP'

    def get_samples(self):
        with self.ssh_connection() as cmd:
            cmd('')     # initial prompt
            vlanoutput = cmd('show vlans')
            portoutput = cmd('show interfaces brief', 5)

        # shoddy port parser
        portlines = filter(lambda s: '|' in s, filter(lambda s: len(s) > 1, portoutput[10:]))
        ports = map(str.split, portlines)
        freeports = len(filter(lambda p: p[5] == 'Down', ports))
        totalports = len(ports)

        # read vlan parser
        vlanlist = False
        maxvlans = 0
        numvlans = 0
        for vline in vlanoutput:
            if 'Maximum VLANs' in vline:
                _, maxvlans = vline.split(':', 1)
                maxvlans = int(maxvlans)
            elif vlanlist:
                if 'No' in vline:
                    numvlans += 1
            elif '-----' in vline:
                vlanlist = True

        return [make_sample(self.site, self.deployment, self.vendor, 'procurve', self.name, {
            'vlans': {
                'max': maxvlans,
                'free': max(maxvlans - numvlans, 0),
            },
            'ports': {
                'total': totalports,
                'free': freeports,
            }
        })]
