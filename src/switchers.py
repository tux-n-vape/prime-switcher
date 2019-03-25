import os
import re

from abc import ABC, abstractmethod
import utils

modprobe_file = '/etc/modprobe.d/prime-switcher.conf'
module_file = '/etc/modules-load.d/prime-switcher.conf'
xorg_file = '/etc/X11/xorg.conf.d/90-prime-switcher.conf'
profile_file = '/etc/profile.d/prime-switcher.sh'
gdm_file = '/etc/gdm/PreSession/prime-switcher'
lightdm_file = '/etc/lightdm/lightdm.conf'
sddm_file = '/usr/share/sddm/scripts/Xsetup'
display_manager_hook = utils.get_config_filepath('open/display_manager_hook.sh')
modes = ['power-saving', 'performance']


class Switcher(ABC):
    def __init__(self, dirname: str) -> None:
        super().__init__()
        self.__dirname__ = dirname

    @abstractmethod
    def get_icon(self) -> str:
        pass

    @abstractmethod
    def set_dedicated_gpu_state(self, state: bool) -> None:
        pass

    @abstractmethod
    def get_dedicated_gpu_state(self) -> bool:
        pass

    def get_config_file(self, file) -> str:
        return os.path.join(utils.get_config_filepath(self.__dirname__), file)

    def get_current_gpu_name(self) -> str:
        glxinfo = utils.execute_command('glxinfo')
        result = re.search(r'.*OpenGL renderer string:\s*([^\n\r]*)', glxinfo)
        if result:
            return result.group(1)
        else:
            return 'Unknown GPU'

    def patch_file_with_pci_id(self, src: str, dst: str):
        gpu_list = utils.get_gpu_list()
        utils.replace_in_file(src, dst, {"<embedded-gpu>": gpu_list[0].get_pci_id(),
                                         "<dedicated-gpu>": gpu_list[1].get_pci_id()})

    def uninstall(self) -> None:
        utils.remove(profile_file)
        utils.remove(xorg_file)
        utils.remove(module_file)
        utils.remove(modprobe_file)


class NvidiaSwitcher(Switcher):
    def __init__(self) -> None:
        super().__init__('nvidia')

    def get_icon(self) -> str:
        return 'nvidia.png' if self.get_dedicated_gpu_state() else 'intel.png'

    def set_dedicated_gpu_state(self, state: bool):
        gpu = 'nvidia' if state else 'intel'
        utils.create_symlink(self.get_config_file(gpu + '-modprobe.conf'),
                             modprobe_file)
        utils.create_symlink(self.get_config_file(gpu + '-modules.conf'),
                             module_file)
        self.patch_file_with_pci_id(self.get_config_file(gpu + '-xorg.conf'), xorg_file)

        if state:
            utils.create_symlink(self.get_config_file('profile.sh'), profile_file)
        else:
            utils.remove(profile_file)

    def get_dedicated_gpu_state(self) -> bool:
        lsmod = utils.execute_command('lsmod')
        return 'nvidia' in lsmod


class NvidiaReversePrime(NvidiaSwitcher):
    def __init__(self) -> None:
        super().__init__()
        self.__dir_name__ = 'nvidia-reverse-prime'


class OpenSourceDriverSwitcher(Switcher):
    def __init__(self) -> None:
        super().__init__('open')

    def get_icon(self) -> str:
        provider_id = os.getenv('DRI_PRIME', 0)
        gpu_brand = utils.get_gpu_list()[provider_id].get_brand()
        if gpu_brand == 'amd':
            return 'amd_on.png' if provider_id else 'amd_off.png'
        else:
            return gpu_brand + '.png'

    def set_dedicated_gpu_state(self, state: bool) -> None:
        if state:
            utils.create_symlink(self.get_config_file('profile.sh'), profile_file)

            # GDM
            if os.path.exists('/etc/gdm/PreSession/'):
                utils.create_symlink(display_manager_hook, gdm_file)
            # LightDM
            if os.path.exists(lightdm_file):
                utils.replace_in_file(lightdm_file, lightdm_file,
                                      {'#display-setup-script=': ('display-setup-script=' + display_manager_hook)})
            # SDDM
            if os.path.exists(sddm_file) and not utils.file_contains(sddm_file, display_manager_hook):
                utils.write_line_in_file(sddm_file, sddm_file)
        else:
            utils.remove(profile_file)
            self.remove_display_manager_hooks()

    def remove_display_manager_hooks(self) -> None:
        # GDM
        utils.remove(gdm_file)
        # LightDM
        if os.path.exists(lightdm_file):
            utils.replace_in_file(lightdm_file, lightdm_file,
                                  {('display-setup-script=' + display_manager_hook): '#display-setup-script='})
        # SDDM
        if os.path.exists(sddm_file):
            utils.remove_line_in_file(sddm_file, display_manager_hook)

    def get_dedicated_gpu_state(self) -> bool:
        return os.getenv('DRI_PRIME', 0) == 1

    def uninstall(self) -> None:
        super().uninstall()
        self.remove_display_manager_hooks()


class NouveauSwitcher(OpenSourceDriverSwitcher):
    def __init__(self) -> None:
        super().__init__()
        self.__dirname__ = 'nouveau'

    def set_dedicated_gpu_state(self, state: bool) -> None:
        super().set_dedicated_gpu_state(state)
        gpu = 'nouveau' if state else 'intel'
        utils.create_symlink(self.get_config_file(gpu + '-modprobe.conf'),
                             modprobe_file)
        utils.create_symlink(self.get_config_file(gpu + '-modules.conf'),
                             module_file)


class NouveauReversePrimeSwitcher(Switcher):
    def __init__(self) -> None:
        super().__init__('nouveau-reverse-prime')

    def get_icon(self) -> str:
        return 'nvidia.png' if self.get_dedicated_gpu_state() else 'intel.png'

    def set_dedicated_gpu_state(self, state: bool) -> None:
        if state:
            self.patch_file_with_pci_id(self.get_config_file('nouveau-xorg.conf'), xorg_file)
        else:
            utils.remove(xorg_file)

    def get_dedicated_gpu_state(self) -> bool:
        return os.path.exists(xorg_file) and os.path.islink(xorg_file) and os.readlink(
            xorg_file) == self.get_config_file('nouveau-xorg.conf')