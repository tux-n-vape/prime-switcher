import gi

import utils

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3 as appindicator
import switchers

gi.require_version('Notify', '0.7')
from gi.repository import Notify
import gettext
import os

APPINDICATOR_ID = 'prime-switcher'


def reboot(widget, *data):
    os.system('shutdown -r now')


def display_notification(widget, *data):
    if os.system('pkexec /usr/bin/prime-switcher -s {}'.format(data[2])) == 0:
        data[0].show()
    else:
        data[1].show()


def open_gui(switcher: switchers.Switcher):
    gettext.textdomain(APPINDICATOR_ID)

    modes_names = ['Power Saving', 'Performance']

    # Notifications Declaration BEGIN
    Notify.init("Prime Switcher")

    success_notify = Notify.Notification.new("Reboot required", "Reboot is required to apply modifications")
    success_notify.add_action('reboot', 'Reboot now', reboot, None, None)

    error_notify = Notify.Notification.new("Error", "An error as occurred.", "error")

    # Notifications Declaration END

    # Menu BEGIN
    menu = Gtk.Menu()

    item = Gtk.MenuItem('Switch to {}'.format(modes_names[int(not switcher.get_dedicated_gpu_state())]))
    item.connect('activate', display_notification, success_notify, error_notify,
                 switchers.modes[int(not switcher.get_dedicated_gpu_state())])
    menu.append(item)

    menu.append(Gtk.SeparatorMenuItem())

    current_mode = Gtk.MenuItem('Current Mode : {}'.format(modes_names[int(switcher.get_dedicated_gpu_state())]))
    current_mode.set_sensitive(False)
    menu.append(current_mode)

    gpu_name = Gtk.MenuItem(switcher.get_current_gpu_name())
    gpu_name.set_sensitive(False)
    menu.append(gpu_name)

    # Menu END

    indicator = appindicator.Indicator.new(APPINDICATOR_ID, os.path.join(
        utils.get_debug_folder('icons') if os.getenv('DEBUG', 0) else '/usr/share/prime-switcher/', switcher.get_icon()),
                                           appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_menu(menu)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

    menu.show_all()

    Gtk.main()
    Notify.uninit()
