__author__ = 'achmed'

from ....gatherer.interface import GathererPluginInterface
from ....sample import make_sample
from ....iso8601 import get_iso8601_timestamp

from . import traversal

from pyVim.connect import SmartConnect, Disconnect


import logging
logger = logging.getLogger(__name__)


class VCenterGathererPlugin(GathererPluginInterface):
    def __init__(self):
        pass

    def initialize(self, name, plugincfg, devicecfg):
        self.devicecfg = devicecfg
        self.plugincfg = plugincfg
        self.name = name

        self.vchost, self.vcport, self.vcuser,  self.vcpass = self.parse_connstring(self.devicecfg.get('connstring'))
        self.site = self.devicecfg.get('site', 'dev')
        self.deployment = self.devicecfg.get('deployment', 'n/a')
        self.vendor = 'VMWare'

    @staticmethod
    def parse_connstring(connstring):
        scheme, url = connstring.split('://', 1)
        auth, host = url.split('@', 1)
        vcuser, vcpass = auth.split(':', 1)
        vchost, vcport = host.split(':', 1)
        vcport = int(vcport.rstrip('/'))

        return vchost, vcport, vcuser, vcpass,

    def get_samples(self):
        ts = get_iso8601_timestamp()

        vcconn = SmartConnect(host=self.vchost, user=self.vcuser, pwd=self.vcpass, port=self.vcport)

        try:
            propspec = {
                'VirtualMachine': [
                    'name', 'runtime.powerState', 'summary.config.numCpu', 'summary.config.memorySizeMB', 'summary.storage.committed', 'runtime.host',
                    ],
                'HostSystem': [
                    'name', 'summary.hardware', 'datastore', 'network', 'vm',
                    ],
                'Datastore': [
                    'name', 'summary'
                ],
                'ClusterComputeResource': [
                    'name', 'host', 'summary.numCpuCores', 'summary.effectiveMemory', 'summary.totalMemory', 'datastore'
                ],
            }

            vcobjs = traversal.get_object_properties_by_propspec(vcconn, propspec=propspec)
        except:
            logger.exception('couldn\'t retrieve properties')
            raise
        finally:
            Disconnect(vcconn)

        logger.info('got %d objects from vmware' % len(vcobjs))

        return list(self.sample_gen(ts, vcobjs, propspec.keys()))

    def sample_gen(self, ts, vcobjs, motypes):
        # munge responses to be a little easier to work with
        vcobjmap = { k: {} for k in motypes}

        for obj in vcobjs:
            assert hasattr(obj, 'obj')
            assert hasattr(obj.obj, '_wsdlName')
            otype = obj.obj._wsdlName
            assert otype in vcobjmap
            vcobjmap[otype][obj.obj._moId] = {p.name: p.val for p in obj.propSet}

        for k,l in vcobjmap.items():
            logger.info('got %d %ss' % (len(l), k))

        # emit cluster samples
        for cname, cluster in vcobjmap['ClusterComputeResource'].iteritems():
            vmcount = 0

            hosts_in_cluster = map(lambda h: h._moId, cluster['host'])
            for host in hosts_in_cluster:
                if host not in vcobjmap['HostSystem']:
                    logger.warn('did not retrieve host %s in cluster %s' % (host, cname))
                    continue
                else:
                    host = vcobjmap['HostSystem'][host]
                    vmcount += len(host['vm'])

            yield make_sample(self.site, self.deployment, self.vendor, 'vmware.cluster', cluster['name'], {
                'vm': {
                    'curr': vmcount,
                    },
                'cpucores': {
                    'curr': cluster['summary.numCpuCores'],
                    },
                'memory': {
                    'total': cluster['summary.totalMemory'],
                    'effective': cluster['summary.effectiveMemory']
                },
                }, ts)

        # emit datastore samples
        for dname, ds in vcobjmap['Datastore'].iteritems():
            assert 'summary' in ds

            yield make_sample(self.site, self.deployment, self.vendor, 'vmware.datastore', ds['name'], {
                'space': {
                    'free': getattr(ds['summary'], 'freeSpace', None),
                    'uncommitted': getattr(ds['summary'], 'uncommitted', None),
                    'capacity': getattr(ds['summary'], 'capacity', None),
                    }
            }, ts)

        # emit vm samples
        #   make a mapping of virtual machines to clusters
        host_to_cluster = {host._moId: clustername for clustername, cluster in vcobjmap['ClusterComputeResource'].iteritems() for host in cluster['host']}
        vm_to_host = {vmname: vm['runtime.host']._moId for vmname, vm in vcobjmap['VirtualMachine'].iteritems()}

        for vmname, vm in vcobjmap['VirtualMachine'].iteritems():
            if vmname not in vm_to_host:
                logger.warn('vm host and cluster not determined for vm %s' % vmname)
                cluster = None
                vmhost = None
            elif vm_to_host[vmname] not in host_to_cluster:
                logger.warn('cluster not determined for vm %s' % vmname)
                cluster = None
                vmhost = vm_to_host[vmname]
                vmhost = vcobjmap['HostSystem'][vmhost]['name']
            else:
                cluster = host_to_cluster[vm_to_host[vmname]]
                vmhost = vm_to_host[vmname]
                vmhost = vcobjmap['HostSystem'][vmhost]['name']

            yield make_sample(self.site, self.deployment, self.vendor, 'vmware.vm', vm['name'], {
                'cluster': cluster,
                'host': vmhost,
                'powerstate': vm['runtime.powerState'],
                'vcpu': {
                    'total': vm['summary.config.numCpu'],
                    },
                'memory': {
                    'total': vm['summary.config.memorySizeMB'],
                    },
                'storage': {
                    'committed': vm['summary.storage.committed'],
                    },
                }, ts)

        # emit host samples
        for hostname, host in vcobjmap['HostSystem'].iteritems():
            yield make_sample(self.site, self.deployment, self.vendor, 'vmware.host', host['name'], {
                'memory': {
                    'total': getattr(host['summary.hardware'], 'memorySize', None),
                    },
                'cpucores': {
                    'total': getattr(host['summary.hardware'], 'numCpuCores', None),
                    },
                }, ts)
