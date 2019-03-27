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
modes = ['power-saving', 'performance']


class Switcher(ABC):
    def __init__(self, dirname: str) -> None:
        """
        :param dirname: Directory name
        """
        super().__init__()
        self.__dirname__ = dirname

    @abstractmethod
    def get_icon(self) -> str:
        """
        Get icon of current GPU's brand
        :return: icon filename
        """
        pass

    def set_discrete_gpu_state(self, state: bool) -> None:
        """
        Patch the system to use discrete GPU as primary GPU or not
        :param state: true for performance mode (Discrete GPU as primary), false for power saving mode
        """
        # Manjaro specific fix
        utils.remove("/etc/X11/xorg.conf.d/90-mhwd.conf")

    @abstractmethod
    def get_discrete_gpu_state(self) -> bool:
        """
        Get if the discrete GPU is used as primary GPU
        :return: true if the discrete GPU is used as primary GPU
        """
        pass

    def get_config_file(self, file) -> str:
        """
        Get full path with the switcher's config directory
        :param file: config filename
        :return: Full path with the switcher's config directory
        """
        return os.path.join(utils.get_config_filepath(self.__dirname__), file)

    def get_current_gpu_name(self) -> str:
        """
        Get current GPU's name
        :return: Current GPU's name
        """
        glxinfo = utils.execute_command('glxinfo')
        result = re.search(r'.*OpenGL renderer string:\s*([^\n\r]*)', glxinfo)
        if result:
            return result.group(1)
        else:
            return 'Unknown GPU'

    def patch_file_with_pci_id(self, src: str, dst: str) -> None:
        """
        Generate config with the PCI ids of GPUs installed on the system
        :param src: Original config file (template)
        :param dst: Destination file
        """
        gpu_list = utils.get_gpu_list()
        utils.replace_in_file(src, dst, {"<embedded-gpu>": gpu_list[0].get_pci_id(),
                                         "<dedicated-gpu>": gpu_list[1].get_pci_id()})

    def uninstall(self) -> None:
        """
        Remove config files of current switcher
        """

    def get_display_manager_hook_file_path(self) -> str:
        """
        Get the display manager hooks script's filepath
        :return: Display manager hooks script's filepath
        """
        return utils.get_config_filepath(self.__dirname__ + '/display_manager_hook.sh')

    def apply_display_manager_hooks(self) -> None:
        """
        Apply hooks on display managers
        """
        if os.path.exists(self.get_display_manager_hook_file_path()):
            # GDM
            if os.path.exists('/etc/gdm/PreSession/'):
                utils.create_symlink(self.get_display_manager_hook_file_path(), gdm_file)
            # LightDM
            if os.path.exists(lightdm_file):
                utils.replace_in_file(lightdm_file, lightdm_file,
                                      {'#display-setup-script=': (
                                              'display-setup-script=' + self.get_display_manager_hook_file_path())})
            # SDDM
            if os.path.exists(sddm_file) and not utils.file_contains(sddm_file,
                                                                     self.get_display_manager_hook_file_path()):
                utils.write_line_in_file(sddm_file, sddm_file)

    def remove_display_manager_hooks(self) -> None:
        """
        Remove hooks on display managers
        """
        if os.path.exists(self.get_display_manager_hook_file_path()):
            # GDM
            utils.remove(gdm_file)
            # LightDM
            if os.path.exists(lightdm_file):
                utils.replace_in_file(lightdm_file, lightdm_file,
                                      {(
                                               'display-setup-script=' + self.get_display_manager_hook_file_path()): '#display-setup-script='})
            # SDDM
            if os.path.exists(sddm_file):
                utils.remove_line_in_file(sddm_file, self.get_display_manager_hook_file_path())


class NvidiaSwitcher(Switcher):
    def __init__(self) -> None:
        super().__init__('nvidia')

    def get_icon(self) -> str:
        return 'nvidia.png' if self.get_discrete_gpu_state() else 'intel.png'

    def set_discrete_gpu_state(self, state: bool):
        super().set_discrete_gpu_state(state)
        gpu = 'nvidia' if state else 'intel'
        utils.create_symlink(self.get_config_file(gpu + '-modprobe.conf'),
                             modprobe_file)
        utils.create_symlink(self.get_config_file(gpu + '-modules.conf'),
                             module_file)
        self.patch_file_with_pci_id(self.get_config_file(gpu + '-xorg.conf'), xorg_file)

        if state:
            utils.create_symlink(self.get_config_file('profile.sh'), profile_file)
            self.apply_display_manager_hooks()
        else:
            utils.remove(profile_file)
            self.remove_display_manager_hooks()

    def get_discrete_gpu_state(self) -> bool:
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
        provider_id = int(os.getenv('DRI_PRIME', 0))
        gpu_brand = utils.get_gpu_list()[provider_id].get_brand()
        if gpu_brand == 'amd':
            return 'amd_on.png' if provider_id else 'amd_off.png'
        else:
            return gpu_brand + '.png'

    def set_discrete_gpu_state(self, state: bool) -> None:
        super().set_discrete_gpu_state(state)
        if state:
            utils.create_symlink(self.get_config_file('profile.sh'), profile_file)
            self.apply_display_manager_hooks()
        else:
            utils.remove(profile_file)
            self.remove_display_manager_hooks()

    def get_discrete_gpu_state(self) -> bool:
        return int(os.getenv('DRI_PRIME', 0)) == 1

    def uninstall(self) -> None:
        super().uninstall()
        self.remove_display_manager_hooks()


class NouveauSwitcher(OpenSourceDriverSwitcher):
    def __init__(self) -> None:
        super().__init__()
        self.__dirname__ = 'nouveau'

    def set_discrete_gpu_state(self, state: bool) -> None:
        super().set_discrete_gpu_state(state)
        gpu = 'nouveau' if state else 'intel'
        utils.create_symlink(self.get_config_file(gpu + '-modprobe.conf'),
                             modprobe_file)
        utils.create_symlink(self.get_config_file(gpu + '-modules.conf'),
                             module_file)


class NouveauReversePrimeSwitcher(Switcher):
    def __init__(self) -> None:
        super().__init__('nouveau-reverse-prime')

    def get_icon(self) -> str:
        return 'nvidia.png' if self.get_discrete_gpu_state() else 'intel.png'

    def set_discrete_gpu_state(self, state: bool) -> None:
        super().set_discrete_gpu_state(state)
        if state:
            self.patch_file_with_pci_id(self.get_config_file('nouveau-xorg.conf'), xorg_file)
        else:
            utils.remove(xorg_file)

    def get_discrete_gpu_state(self) -> bool:
        return os.path.exists(xorg_file) and os.path.islink(xorg_file) and os.readlink(
            xorg_file) == self.get_config_file('nouveau-xorg.conf')
