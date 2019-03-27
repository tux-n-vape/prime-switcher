#!/usr/bin/env python3

import argparse
import gui
import utils
import switchers
import os
import gettext


def detect_driver() -> str:
    """Detect the best driver installed on the system and return its name"""
    gpu_list = utils.get_gpu_list()
    driver = 'free'
    if gpu_list[0].get_brand() == 'intel' and gpu_list[1].get_brand() == 'nvidia':
        non_free_driver = os.path.exists('/usr/bin/nvidia-modprobe')
        driver = 'nvidia' if non_free_driver else 'nouveau'
        if gpu_list[1].has_screen():
            driver += '-reverse-prime'
    print('Target driver detected : {}'.format(driver))
    return driver


def run_as_root(func, *args, **kwargs) -> None:
    """Check if user is root and execute given function else PermissionError"""
    if os.getuid() == 0:
        func(*args, **kwargs)
    else:
        raise PermissionError('Root permissions are required.')


def main():
    current_driver_file = utils.get_config_filepath('current-driver')

    localedir = utils.get_debug_path('locales') if os.getenv('DEBUG', 0) else None
    gettext.install('prime-switcher', localedir=localedir)

    with open(current_driver_file, 'r') as f:
        config_driver = f.readline().rstrip('\n')

    switchers_dict = {'free': switchers.OpenSourceDriverSwitcher(), 'nvidia': switchers.NvidiaSwitcher(),
                      'nvidia-reverse-prime': switchers.NvidiaReversePrime(), 'nouveau': switchers.NouveauSwitcher(),
                      'nouveau-reverse-prime': switchers.NouveauReversePrimeSwitcher()}

    parser = argparse.ArgumentParser(prog='prime-switcher')
    parser.add_argument('--set', '-s', type=str, choices=switchers.modes)
    parser.add_argument('--driver', '-d', type=str, choices=switchers_dict.keys(), default=config_driver)
    parser.add_argument('--uninstall', '-u', action='store_true')
    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--query', '-q', action='store_true')
    parser.add_argument('--detect', '-D', action='store_true')
    args = parser.parse_args()

    swr = switchers_dict[args.driver]
    if args.gui:
        gui.open_gui(swr)
    elif args.query:
        gpu = 'Performance' if swr.get_discrete_gpu_state() else 'Power Saving'
        print('Targeted Driver :', config_driver)
        print('Current Mode :', gpu)
        print('GPU :', swr.get_current_gpu_name())
    elif args.uninstall:
        print('Uninstalling...')
        run_as_root(swr.uninstall)
        print('Done.')
    elif args.set is not None:
        if args.detect:
            args.driver = detect_driver()
            swr = switchers_dict[args.driver]
        if args.driver != config_driver:
            print('Uninstalling config for previous driver...')
            run_as_root(switchers_dict[config_driver].uninstall)
            with open(current_driver_file, 'w') as f:
                f.write(args.driver)
        print('Configuring...')
        run_as_root(swr.set_discrete_gpu_state, args.set == 'performance')
        print('Done. Reboot required to apply changes.')
    elif args.detect:
        detect_driver()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
