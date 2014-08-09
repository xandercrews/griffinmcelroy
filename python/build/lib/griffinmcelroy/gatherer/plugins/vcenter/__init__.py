__author__ = 'achmed'

from ....gatherer.interface import GathererPluginInterface
from ....sample import make_sample
from ....iso8601 import get_iso8601_timestamp

# from pyVmomi import vim, vmomi

class VCenterGathererPlugin(GathererPluginInterface):
    def __init__(self):
        pass

    def initialize(self, config):
        self.vchost = config.get('vchost', 'vcenter')
        self.vcpass = config.get('vcport', 443)
        self.vcuser = config.get('vcuser', 'root')
        self.vcpass = config.get('vcpass', 'vmware')
        self.site = config.get('site', 'dev')
        self.deployment = config.get('site', 'n/a')
        self.vendor = 'VMWare'

    def get_samples(self):
        timestamp = get_iso8601_timestamp()

        return [
            make_sample(self.site, self.deployment, self.vendor, 'vm.cpu.used', 'bacon1', { 'percentage': 100.0, 'hz': 1200.0, }, timestamp),
            make_sample(self.site, self.deployment, self.vendor, 'vm.cpu.free', 'bacon1', { 'percentage': 0.0, 'hz': 0.0, }, timestamp),
            make_sample(self.site, self.deployment, self.vendor, 'vm.memory.used', 'bacon1', { 'amount': 1244213, }, timestamp),
            make_sample(self.site, self.deployment, self.vendor, 'vm.memory.free', 'bacon1', { 'amount': 852939, }, timestamp),
        ]