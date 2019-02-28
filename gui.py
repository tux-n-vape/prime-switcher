import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3 as appindicator
import switchers
import gettext

APPINDICATOR_ID = 'prime-switcher'
ICON_FOLDER_PATH = '/usr/share/prime-switcher/'


def open_gui(switcher: switchers.Switcher):
    menu = Gtk.Menu()

    item = Gtk.MenuItem('Switch to ')
    menu.append(item)

    menu.append(Gtk.SeparatorMenuItem())

    current_mode = Gtk.MenuItem('Current Mode : Performance')
    current_mode.set_sensitive(False)
    menu.append(current_mode)

    gpu_name = Gtk.MenuItem(switcher.get_current_gpu_name())
    gpu_name.set_sensitive(False)
    menu.append(gpu_name)

    indicator = appindicator.Indicator.new(APPINDICATOR_ID, ICON_FOLDER_PATH + switcher.get_icon(),
                                           appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_menu(menu)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

    menu.show_all()

    Gtk.main()
