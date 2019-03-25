#!/bin/bash

find locales -name \*.po -execdir msgfmt prime-switcher.po -o prime-switcher.mo

mkdir -p /etc/prime-switcher/
cp -r configs/* /etc/prime-switcher/
mkdir -p /usr/lib/prime-switcher/
mkdir -p /usr/share/prime-switcher/
cp icons/* /usr/share/prime-switcher/
cp gpu.py gui.py __main__.py utils.py switchers.py /usr/lib/prime-switcher/
ln -s /usr/lib/prime-switcher/__main__.py /usr/bin/prime-switcher
cp app-icon/* /usr/share/icons/hicolor/
cp prime-switcher.desktop /etc/xdg/autostart/

cd locales
find . -name '*.mo' -exec cp --parents \{\} ${pkgdir}/usr/share/locales/ \;