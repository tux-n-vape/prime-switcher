#!/bin/env python3

import argparse
import switchers
import gui
import os

default_driver = 'free'


def run_as_root(func, args, kwargs):
    if os.getuid() == 0:
        func(*args, **kwargs)
    else:
        print('Root is required')


if __name__ == '__main__':
    switchers_dict = {'free': switchers.OpenSourceDriverSwitcher(), 'nvidia': switchers.NvidiaSwitcher()}

    parser = argparse.ArgumentParser(prog='prime-switcher')
    parser.add_argument('--set', '-s', type=str, choices=['power-saving', 'performance'])
    parser.add_argument('--driver', '-d', type=str, choices=switchers_dict.keys(), default=default_driver)
    parser.add_argument('--uninstall', action='store_true')
    parser.add_argument('--gui', action='store_true')

    args = parser.parse_args()
    if args.gui:
        gui.open_gui()
    else:
        swr = switchers_dict[args.driver]

        if args.uninstall:
            run_as_root(swr.uninstall)
        elif args.set is not None:
            run_as_root(swr.set_dedicated_gpu_state, args.set == 'performance')
        else:
            parser.print_help()
