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

    with open(current_driver_file, 'r') as f:
        default_driver = f.readline().rstrip('\n')

    switchers_dict = {'free': switchers.OpenSourceDriverSwitcher(), 'nvidia': switchers.NvidiaSwitcher()}

    parser = argparse.ArgumentParser(prog='prime-switcher')
    parser.add_argument('--set', '-s', type=str, choices=['power-saving', 'performance'])
    parser.add_argument('--driver', '-d', type=str, choices=switchers_dict.keys(), default=default_driver)
    parser.add_argument('--uninstall', '-u', action='store_true')
    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--query', '-q', action='store_true')

    args = parser.parse_args()
    swr = switchers_dict[args.driver]
    if args.gui:
        gui.open_gui()
    elif args.query:
        gpu = 'Performance' if swr.get_dedicated_gpu_state() else 'Power Saving'
        print('Targeted Driver :', default_driver)
        print('Current Mode :', gpu)
        print('GPU :', swr.get_current_gpu_name())
    else:
        if args.uninstall:
            print('Uninstalling...')
            run_as_root(swr.uninstall)
            print('Done.')
        elif args.set is not None:
            if args.driver != default_driver:
                print('Uninstalling config for previous driver...')
                run_as_root(switchers_dict[default_driver].uninstall)
                with open(current_driver_file, 'w') as f:
                    f.write(args.driver)
            print('Configuring...')
            run_as_root(swr.set_dedicated_gpu_state, args.set == 'performance')
            print('Done. Reboot required to apply changes.')
        else:
            parser.print_help()
