__author__ = 'achmed'

import collections


def get_version_string():
    version = get_version()

    if isinstance(version, (basestring, unicode,)):
        return version
    elif isinstance(version, collections.Sequence):
        return '.'.join(version)
    return str(version)


def get_version():
    try:
        from .version import VERSION
        return VERSION
    except ImportError:
        return 'dev'
