#!/bin/bash

find locales -name \*.po -execdir msgfmt prime-switcher.po -o prime-switcher.mo

mkdir -p /etc/prime-switcher/
mkdir -p /usr/lib/prime-switcher/
mkdir -p /usr/share/prime-switcher/

cp -r configs/* /etc/prime-switcher/
cp assets/* /usr/share/prime-switcher/
cp src/* /usr/lib/prime-switcher/
cp icons/* /usr/share/icons/hicolor/
cp prime-switcher.desktop /etc/xdg/autostart/

ln -s /usr/lib/prime-switcher/__main__.py /usr/bin/prime-switcher

cd locales
find . -name '*.mo' -exec cp --parents \{\} ${pkgdir}/usr/share/locales/ \;