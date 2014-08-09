__author__ = 'achmed'

import datetime


def get_iso8601_timestamp(tz='UTC'):
    if tz == 'UTC':
        return str(datetime.datetime.utcnow().isoformat()) + 'Z'
    else:
        return str(datetime.datetime.now(tz).isoformat()) + 'Z'