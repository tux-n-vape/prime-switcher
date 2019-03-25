# Maintainer: Adrien Jussak <adrien.jussak@wascardev.com>

_name='prime-switcher'
pkgname="${_name}-git"
pkgver=0.1
pkgrel=1
pkgdesc="Tool (GUI  + CLI) to select used GPU for Optimus Laptop"
arch=('any')
url='https://gitlab.com/tuxnvape/prime-switcher'
depends=('python-gobject' 'libappindicator-gtk3' 'gtk3' 'libnotify' 'mesa-demos' 'gettext')
optdepends=('bbswitch: For power saving with NVIDIA discrete GPU')
license=('GPLv3')
conflicts=('prime-switcher')
install=prime-switcher.install

source=("git+https://gitlab.com/tuxnvape/prime-switcher.git")

sha256sums=(SKIP)

build() {
	_src="${srcdir}/prime-switcher"
    find ${_src}/locales -name \*.po -execdir msgfmt prime-switcher.po -o prime-switcher.mo \;
}

package() {
	_src="${srcdir}/prime-switcher"
    mkdir -p ${pkgdir}/usr/share/${_name}
    mkdir -p ${pkgdir}/usr/lib/${_name}
    mkdir -p ${pkgdir}/etc/${_name}
    mkdir -p ${pkgdir}/usr/share/locales
    mkdir -p ${pkgdir}/usr/bin
    mkdir -p ${pkgdir}/usr/share/icons/hicolor/

    cp -r ${_src}/configs/* ${pkgdir}/etc/${_name}/
    cp -r ${_src}/assets/* ${pkgdir}/usr/share/${_name}
    cp ${_src}/src/* ${pkgdir}/usr/lib/${_name}
    cp -r ${_src}/icons/* ${pkgdir}/usr/share/icons/hicolor/
    ln -s ../lib/${_name}/__main__.py ${pkgdir}/usr/bin/${_name}
    cp ${_src}/prime-switcher.desktop ${pkgdir}/etc/xdg/autostart/
    
   	cd ${_src}/locales/
    find . -name '*.mo' -exec cp --parents \{\} ${pkgdir}/usr/share/locales/ \;
}

