__author__ = 'achmed'

import time
import contextlib


import paramiko


from ...interface import GathererPluginInterface
from ....config.configwrapper import ConfigWrapper


import logging
logger = logging.getLogger(__name__)


# import paramiko.common
# paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)


class GenericSSHGathererPlugin(GathererPluginInterface):
    def initialize(self, name, plugincfg, devicecfg):
        self.devicecfg = ConfigWrapper(other=devicecfg)
        self.plugincfg = ConfigWrapper(other=plugincfg)
        self.name = name

        self.deployment = self.devicecfg.get('deployment', 'n/a')
        self.site = self.devicecfg.get('site', 'dev')

        self.sshhost, self.sshport, self.sshuser, self.sshpass =  self.parse_connstring(self.devicecfg.get('connstring'))

    @contextlib.contextmanager
    def ssh_simple_connection(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.sshhost, username=self.sshuser, password=self.sshpass, port=self.sshport)
        def do_cmd(cmdstring):
            stdin, stdout, stderr = client.exec_command(cmdstring)
            return stdout.read(), stderr.read()
        yield do_cmd
        client.close()

    @contextlib.contextmanager
    def ssh_connection(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.sshhost, username=self.sshuser, password=self.sshpass, port=self.sshport, allow_agent=False)
        channel = client.invoke_shell(width=150, height=75)
        channel.setblocking(0)
        channel.settimeout(30)
        def do_cmd(cmd, sleep=2):
            logger.debug('sending cmd: ' + cmd)
            channel.send(cmd + '\n')
            time.sleep(sleep)
            output = ''
            while channel.recv_ready():
                output += channel.recv(1024)
            logger.debug('got output: ' + output)
            return output.splitlines()[1:]
        yield do_cmd
        channel.close()

    def parse_connstring(self, connstring):
        scheme, url = connstring.split('://', 1)
        auth, host = url.split('@', 1)
        sshuser, sshpass = auth.split(':', 1)
        sshhost, sshport = host.split(':', 1)
        sshport = int(sshport.rstrip('/'))

        return sshhost, sshport, sshuser, sshpass
