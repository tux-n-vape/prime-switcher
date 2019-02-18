import os
import re

from abc import ABC, abstractmethod
import utils

modprobe_file = '/etc/modprobe.d/prime-switcher.conf'
module_file = '/etc/modules-load.d/prime-switcher.conf'
xorg_file = '/etc/X11/xorg.conf.d/90-prime-switcher.conf'
profile_file = '/etc/profile.d/prime-switcher.sh'


class Switcher(ABC):
    @abstractmethod
    def get_icon(self) -> str:
        pass

    @abstractmethod
    def set_dedicated_gpu_state(self, state: bool):
        pass

    @abstractmethod
    def get_dedicated_gpu_state(self) -> bool:
        pass

    def get_current_gpu_name(self) -> str:
        glxinfo = utils.execute_command('glxinfo')
        result = re.search(r'.*OpenGL renderer string:\s*([^\n\r]*)', glxinfo)
        if result:
            return result.group(1)
        else:
            return 'Unknown GPU'

    @abstractmethod
    def get_reboot_required(self) -> bool:
        pass


class NvidiaSwitcher(Switcher):
    def get_icon(self) -> str:
        return 'nvidia.png' if self.get_dedicated_gpu_state() else 'intel.png'

    def set_dedicated_gpu_state(self, state: bool):
        gpu = 'nvidia' if state else 'intel'
        utils.create_symlink(utils.get_config_filepath('nvidia/' + gpu + '-modprobe.conf'),
                             modprobe_file)
        utils.create_symlink(utils.get_config_filepath('nvidia/' + gpu + '-modules.conf'),
                             module_file)
        utils.create_symlink(utils.get_config_filepath('nvidia/' + gpu + '-xorg.conf'),
                             xorg_file)

        if state:
            utils.create_symlink(utils.get_config_filepath('nvidia/profile.sh'), profile_file)
        else:
            os.remove('/etc/profile.d/prime-switcher.sh')

    def get_dedicated_gpu_state(self) -> bool:
        lsmod = utils.execute_command('lsmod')
        return 'nvidia' in lsmod

    def get_reboot_required(self) -> bool:
        return True


class OpenSourceDriverSwitcher(Switcher):
    def get_icon(self) -> str:
        provider_id = os.getenv('DRI_PRIME', 0)
        provider_list = utils.execute_command('xrandr --listproviders')
        result = re.search(r'.*Provider ' + provider_id + r':\s*(.*name:*([^\n\r]*))', provider_list)
        if result:
            driver_name = result.group(2)
            if driver_name in ['amdgpu', 'radeon']:
                return 'amd_on.png' if provider_id else 'amd_off.png'
            elif driver_name == 'nouveau':
                return 'nvidia.png'
            elif driver_name == 'intel':
                return 'intel.png'
        return 'unknown.png'

    def set_dedicated_gpu_state(self, state: bool):
        gdm_file = '/etc/gdm/PreSession/prime-switcher'
        lightdm_file = '/etc/lightdm/lightdm.conf'
        sddm_file = '/usr/share/sddm/scripts/Xsetup'

        display_manager_hook = utils.get_config_filepath('open/display_manager_hook.sh')

        if state:
            utils.create_symlink(utils.get_config_filepath('open/profile.sh'), profile_file)
            try:
                os.remove(modprobe_file)
                os.remove(module_file)
            except FileNotFoundError:
                pass

            # GDM
            if os.path.exists('/etc/gdm/PreSession/'):
                utils.create_symlink(display_manager_hook, gdm_file)
            # LightDM
            if os.path.exists(lightdm_file):
                utils.replace_in_file(lightdm_file, '#display-setup-script=',
                                      'display-setup-script=' + display_manager_hook)
            # SDDM
            if os.path.exists(sddm_file) and not utils.file_contains(sddm_file, display_manager_hook):
                utils.write_line_in_file(sddm_file, sddm_file)
        else:
            try:
                os.remove(profile_file)
            except FileNotFoundError:
                pass
            utils.create_symlink(utils.get_config_filepath('open/gpuoff-modprobe.conf'), modprobe_file)
            utils.create_symlink(utils.get_config_filepath('open/gpuoff-module.conf'), module_file)
            try:
                os.remove(gdm_file)
                if os.path.exists(lightdm_file):
                    utils.replace_in_file(lightdm_file, 'display-setup-script=' + display_manager_hook,
                                          '#display-setup-script=')
                if os.path.exists(sddm_file):
                    utils.remove_line_in_file(sddm_file, display_manager_hook)

            except FileNotFoundError:
                pass

    def get_dedicated_gpu_state(self) -> bool:
        return os.getenv('DRI_PRIME', 0) == 1

    def get_reboot_required(self) -> bool:
        return False
