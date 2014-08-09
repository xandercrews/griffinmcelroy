__author__ = 'achmed'

import sys
import argparse


def get_opts(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', required=True, type=argparse.FileType('r'), help='a \'config\' file from the pypi module called \'config\'')
    return parser.parse_args(args)
