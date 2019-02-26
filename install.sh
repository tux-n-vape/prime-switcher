#!/bin/bash

mkdir -p /etc/prime-switcher/
cp configs/* /etc/prime-switcher/
mkdir -p /usr/lib/prime-switcher/
cp gui.py prime-switcher.py utils.py switchers.py /usr/lib/prime-switcher/
ln -s /usr/lib/prime-switcher/prime-switcher.py /usr/bin/prime-switcher