__author__ = 'achmed'

import time

import logging
logger = logging.getLogger(__name__)


class SkewlessScheduler(object):
    def __init__(self, interval):
        if not isinstance(interval, (float, int)):
            raise Exception('scheduler interval is required')

        self.interval = float(interval)

    def schedule_generator(self):
        now = time.time()
        last = now

        yield now

        while True:
            now = time.time()

            while last < now:
                last += self.interval

            while now < last:
                tdelta = last - now
                time.sleep(tdelta)
                now = time.time()

            yield now


if __name__ == '__main__':
    ss = SkewlessScheduler(1.0)
    count = 1

    for t in ss.schedule_generator():
        count += 1
        if count >= 5:
            break
        print t

    print 'done'
