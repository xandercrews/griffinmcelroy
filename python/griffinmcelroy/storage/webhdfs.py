
__author__ = 'achmed'

import os
import sys
import glob
import errno
import atexit
import datetime

from .interface import SampleStorageInterface
from ..webhdfs import WebHDFS
from ..sample import GriffinSample
from ..config.configwrapper import ConfigWrapper

from logging.handlers import RotatingFileHandler

import logging
logger = logging.getLogger(__name__)


class WebHDFSSampleStorageBackend(SampleStorageInterface):
    def initialize(self, storagecfg):
        cfg = self.cfg = ConfigWrapper(other=storagecfg.get('webhdfs'))
        self.scratchdir = cfg.getByPath('scratch.dir', '/tmp/webhdfs/')
        self.scratchfilename = cfg.getByPath('scratch.filename', 'samples')
        self.scratchfilelimitkb = cfg.getByPath('scratch.filelimitkb', 2048)
        self.scratchbackupcount = cfg.getByPath('scratch.backupcount', 2)
        self.version = cfg.get('version', 'v1')
        self.username = cfg.getByPath('hadoop.username', 'root')
        self.docker = cfg.get('docker', False)

        if self.docker:
            self.nameport = cfg.getByPath('hadoop.nameport', 57070) # nameport must proceed namehost
            self.dataport = cfg.getByPath('hadoop.dataport', 57075) # dataport must proceed datahost
            self.namehost = self._detect_hadoop_namehost()
            self.datahost = self._detect_hadoop_datahost()
            self.nameport = self._detect_hadoop_nameport()
            self.dataport = self._detect_hadoop_dataport()
        else:
            self.nameport = cfg.getByPath('hadoop.nameport', 57070)
            self.namehost = cfg.getByPath('hadoop.namehost')
            self.dataport = cfg.getByPath('hadoop.dataport', 57075)
            self.datahost = cfg.getByPath('hadoop.datahost')

        self.hadoopmethod = cfg.getByPath('hadoop.method', 'http')
        self.remotedir = cfg.get('remotedir', '/griffinmcelroy/')

        if None in (self.datahost, self.namehost):
            raise Exception('could not determine webhdfs connection host(s)')

        self._make_scratch_dir()

        self.webhdfs = WebHDFS(self.namehost, self.nameport, self.datahost, self.dataport, self.username)

        self.scratchfile = None
        self._open_scratch_file()
        atexit.register(self._close_scratch_file)

        self._ensure_target_dir()

    def flush(self):
        self._close_scratch_file()

    def __del__(self):
        self._close_scratch_file()

    def _close_scratch_file(self):
        if self.scratchfile:
            self.scratchfile.close()
            self.scratchfile = None

    def _open_scratch_file(self):
        if not self.scratchfile:
            scratchpath = os.path.join(self.scratchdir, self.scratchfilename)
            self.scratchfile = RotatingSampleFile(self._persist_full_samples_file, scratchpath, mode='w', maxBytes=self.scratchfilelimitkb*1024, backupCount=self.scratchbackupcount)

    def persist_samples(self, samples):
        self._open_scratch_file()
        for sample in samples:
            self.scratchfile.emit(sample)

    def _detect_hadoop_namehost(self):
        HADOOP_NAME_HOST  = os.environ.get('HADOOP_PORT_%d_TCP_ADDR' % self.nameport, None)
        return HADOOP_NAME_HOST

    def _detect_hadoop_nameport(self):
        HADOOP_NAME_PORT = os.environ.get('HADOOP_PORT_%d_TCP_PORT' % self.nameport, 57070)
        return HADOOP_NAME_PORT

    def _detect_hadoop_datahost(self):
        HADOOP_DATA_HOST  = os.environ.get('HADOOP_PORT_%d_TCP_ADDR' % self.dataport, None)
        return HADOOP_DATA_HOST

    def _detect_hadoop_dataport(self):
        HADOOP_DATA_PORT = os.environ.get('HADOOP_PORT_%d_TCP_PORT' % self.dataport, 57070)
        return HADOOP_DATA_PORT

    def _make_scratch_dir(self):
        try:
            os.makedirs(self.scratchdir)
        except OSError, e:
            if e.errno == errno.EEXIST:
                pass
            else:
                errinfo = sys.exc_info()
                try:
                    raise e, None, errinfo[2]
                except None:
                    pass
                finally:
                    del errinfo

    def _resolve_scratch_path(self, filename):
        return os.path.join(self.scratchdir, filename)

    def _persist_full_samples_file(self, filename):
        assert os.path.isfile(filename)
        remotefilename = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f.json')
        remotepath = os.path.join(self.remotedir, remotefilename)
        self.webhdfs.copyFromLocal(filename, remotepath)

    def _ensure_target_dir(self):
        comps = filter(lambda s: len(s), self.remotedir.split('/'))

        if len(comps) == 1:
            self.webhdfs.mkdir('/' + comps[0])
        else:
            for end in reversed(range(-len(comps), 1)):
                pathsegment = '/' + '/'.join(comps[0:end])
                self.webhdfs.mkdir(pathsegment)


class RotatingSampleFile(RotatingFileHandler):
    '''
    borrow log rotating file handler to get a file roller for samples
    '''

    def __init__(self, callback, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        logger.info('mode: %s filename: %s' % (mode, filename))
        self._remove_previous_files(filename)    # there is a problem with the rotatingfilehandler where it doesn't honor the mode
        super(RotatingSampleFile, self).__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.callback = callback

    @staticmethod
    def _remove_previous_files(filename):
        try:
            os.unlink(filename)
        except OSError, e:
            pass

        scratchfiles = glob.glob(filename + '.*')
        for path in scratchfiles:
            try:
                os.unlink(path)
            except OSError, e:
                pass

    def emit(self, sample, callback=None):
        if self.shouldRollover(sample):
            self.doRollover(callback)
        self.stream.write(self.format(sample) + "\n")
        self.flush()

    def doRollover(self, callback=None):
        newfile = self.get_old_filename() + '.1'
        logger.debug('doing rollover')
        RotatingFileHandler.doRollover(self)
        if newfile is not None:
            if callback is None:
                self.callback(newfile)
            else:
                callback(newfile)

    def close(self, callback=None):
        oldfile = self.get_old_filename()
        logger.debug('closing')
        super(RotatingSampleFile, self).close()
        if oldfile is not None:
            if callback is None:
                self.callback(oldfile)
            else:
                callback(oldfile)

    def format(self, sample):
        logger.debug('did format')
        assert isinstance(sample, GriffinSample)
        j =  sample.to_json()
        assert '\n' not in j
        return j

    def get_old_filename(self):
        if self.stream is None:
            return None
        return self.stream.name
