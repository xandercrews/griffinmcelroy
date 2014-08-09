__author__ = 'achmed'

import config


class ConfigWrapper(config.Config):
    '''
    use to bless config.Mapping objects into Config objects to provide getByPath
    '''
    def __init__(self, streamOrFile=None, parent=None, other=None):
        if other:
            super(ConfigWrapper, self).__init__()
            object.__setattr__(self, 'path', other.path)
            object.__setattr__(self, 'data', other.data)
            object.__setattr__(self, 'order', other.order)
            object.__setattr__(self, 'comments', other.comments)
        else:
            super(ConfigWrapper, self).__init__(streamOrFile=streamOrFile, parent=parent)

    def getByPath(self, path, default=None):
        try:
            return super(ConfigWrapper, self).getByPath(path)
        except config.ConfigError:
            return default