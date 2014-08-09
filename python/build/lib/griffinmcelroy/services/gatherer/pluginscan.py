__author__ = 'achmed'

import pkg_resources

def scan_gatherer_plugins():
    for ep in pkg_resources.iter_entry_points(group='griffinmcelroy.gatherer'):
        print ep
        pass


if __name__ == '__main__':
    scan_gatherer_plugins()
