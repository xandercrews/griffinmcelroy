__author__ = 'achmed'

import os

from ...interface import GathererPluginInterface
from ....config.configwrapper import ConfigWrapper
from ....sample import make_sample

from pysnmp.entity.rfc3413.oneliner import cmdgen

import logging
logger = logging.getLogger(__name__)


class DemoSNMPGathererPlugin(GathererPluginInterface):
    def initialize(self, name, plugincfg, devicecfg):
        self.devicecfg = ConfigWrapper(other=devicecfg)
        self.plugincfg = ConfigWrapper(other=plugincfg)
        self.name = name

        self.deployment = self.devicecfg.get('deployment', 'n/a')
        self.site = self.devicecfg.get('site', 'dev')
        self.vendor = 'Linux'

        self.snmphost = os.environ.get('SNMP_PORT_161_UDP_ADDR')
        self.snmpport = int(os.environ.get('SNMP_PORT_161_UDP_PORT'))
        self.community = self.devicecfg.get('community', 'public')

    def get_samples(self):
        errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().getCmd(
            cmdgen.CommunityData(self.community),
            cmdgen.UdpTransportTarget((self.snmphost, self.snmpport)),
            '.1.3.6.1.2.1.1.5.0',
            '.1.3.6.1.2.1.25.2.2.0',
            '.1.3.6.1.2.1.25.2.3.1.6.1',
        )

        if errorIndication:
            raise Exception(errorIndication)
        elif errorStatus:
            raise Exception(errorStatus)
        else:
            results = dict([(str(k), v._value) for k,v in varBinds])

            hostname = results['1.3.6.1.2.1.1.5.0']
            totalmemory = results['1.3.6.1.2.1.25.2.2.0']
            usedmemory = results['1.3.6.1.2.1.25.2.3.1.6.1']

            return [
                make_sample(self.site, self.deployment, self.vendor, 'linux', hostname, {
                    'memory': {
                        'total': totalmemory,
                        'used': usedmemory,
                    }
                })
            ]
