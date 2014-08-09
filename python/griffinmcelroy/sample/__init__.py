__author__ = 'achmed'

import json

from ..iso8601 import get_iso8601_timestamp


class GriffinSample(object):
    def __init__(self, **kw):
        try:
            self.timestamp = kw.get('timestamp', get_iso8601_timestamp())
            self.site = kw.get('site')
            self.deployment = kw.get('deployment')
            self.vendor = kw.get('vendor')
            self._type = kw.get('_type')
            self._id = kw.get('_id')
            self.data = kw.get('data')
        except KeyError, e:
            raise Exception('missing required field in sample: %s' % str(e))

    def to_dict(self):
        return {
          "timestamp": self.timestamp,
          "site": self.site,
          "deployment": self.deployment,
          "vendor": self.vendor,
          "type": self._type,
          "id": self._id,
          "data": self.data,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, j):
        return GriffinSample(**j)


def make_sample(site, deployment, vendor, _type, _id, data, *args):
    """
    convenience method if you prefer to make samples with positional arguments
    :return: a sample object
    :rtype: GriffinSample
    """

    if len(args) == 0:
        return GriffinSample(site=site, deployment=deployment, vendor=vendor, _type=_type, _id=_id, data=data)
    else:
        assert len(args) == 1, 'only one optional argument of timestamp is allowed'
        return GriffinSample(site=site, deployment=deployment, vendor=vendor, _type=_type, _id=_id, data=data, timestamp=args[0])
