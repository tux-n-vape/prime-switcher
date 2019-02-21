#!/bin/env python3

import argparse
import switchers
import gui
import os
import utils


def run_as_root(func, *args, **kwargs):
    if os.getuid() == 0:
        func(*args, **kwargs)
    else:
        raise PermissionError('Root permissions are required.')


if __name__ == '__main__':
    current_driver_file = utils.get_config_filepath('current-driver')

    with open(current_driver_file) as f:
        default_driver = f.read()

    switchers_dict = {'free': switchers.OpenSourceDriverSwitcher(), 'nvidia': switchers.NvidiaSwitcher()}

    parser = argparse.ArgumentParser(prog='prime-switcher')
    parser.add_argument('--set', '-s', type=str, choices=['power-saving', 'performance'])
    parser.add_argument('--driver', '-d', type=str, choices=switchers_dict.keys(), default=default_driver)
    parser.add_argument('--uninstall', '-u', action='store_true')
    parser.add_argument('--gui', action='store_true')

    args = parser.parse_args()
    if args.gui:
        gui.open_gui()
    else:
        swr = switchers_dict[args.driver]

        if args.uninstall:
            run_as_root(swr.uninstall)
        elif args.set is not None:
            if args.driver != default_driver:
                run_as_root(switchers_dict[default_driver].uninstall)
            run_as_root(swr.set_dedicated_gpu_state, args.set == 'performance')
        else:
            parser.print_help()
