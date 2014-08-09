__author__ = 'achmed'

from .interface import SampleStorageInterface
from .webhdfs import WebHDFSSampleStorageBackend
from .postgres import PostgresSampleStorageBackend


def storage_backend_config_loader(cfg):
    '''
    loads and initializes the correct backend plugin by config
    :param cfg:
    :return:
    '''
    backendtype = cfg.get('backend')

    if backendtype == 'webhdfs':
        backend = WebHDFSSampleStorageBackend()
    elif backendtype == 'postgres':
        backend = PostgresSampleStorageBackend()
    elif backendtype is None:
        raise Exception('storage backend is not configured')
    else:
        raise Exception('unsupported storage backend configured')

    backend.initialize(cfg)
    return backend
