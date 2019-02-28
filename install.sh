#!/bin/bash

mkdir -p /etc/prime-switcher/
cp -r configs/* /etc/prime-switcher/
mkdir -p /usr/lib/prime-switcher/
mkdir -p /usr/share/prime-switcher/
cp icons/* /usr/share/prime-switcher/
cp gui.py prime-switcher.py utils.py switchers.py /usr/lib/prime-switcher/
ln -s /usr/lib/prime-switcher/prime-switcher.py /usr/bin/prime-switcher
