import subprocess
import os
import re
import gpu
from typing import List
from typing import Dict


def execute_command(cmd) -> str:
    """Execute command and return standard output after executing"""
    return subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().decode()


def get_debug_path(path: str) -> str:
    """Concatenate debug folder path and given path"""
    return os.path.join(os.path.dirname(os.getcwd()), path)


def get_config_filepath(file: str) -> str:
    """Concatenate config folder path and given path"""
    return os.path.join(get_debug_path('configs') if os.getenv('DEBUG', 0) else '/etc/prime-switcher/', file)


def get_gpu_list() -> List[gpu.GPU]:
    """Get list of GPU detected by the system (lspci)"""
    data = execute_command('lspci').lower()
    reg = re.compile(r'(vga|display|hdmi|3d)')
    list = []
    for device in data.split('\n'):
        if reg.search(device):
            de = re.search(r'([^ ]*).*:\s*([^ ]*)', device)
            if de:
                has_screen = re.search(r'(vga|display|hdmi)', device)
                pci_id = de.group(1).replace('.', ':')
                list.append(gpu.GPU(pci_id, bool(has_screen), de.group(2)))
    return list


def replace_in_file(src: str, dst: str, correlations: Dict[str, str]) -> None:
    """Copy file and replace given correlations"""
    f = open(src, 'r')
    file_data = f.read()
    f.close()

    for key in correlations:
        file_data = file_data.replace(key, correlations[key])

    # May prevent some problems (like symlink)
    if os.path.exists(dst):
        os.remove(dst)

    f = open(dst, 'w')
    f.write(file_data)
    f.close()


def create_symlink(source: str, dest: str) -> None:
    """Create symlink (Delete exiting file if exists)"""
    if os.path.exists(dest):
        os.remove(dest)
    os.symlink(source, dest)


def file_contains(file: str, text: str) -> bool:
    """Return true if file contains given string"""
    with open(file, 'r') as f:
        data = f.read()
        return text in data


def write_line_in_file(file: str, line: str) -> None:
    """Append given line in a given file"""
    with open(file, 'a') as f:
        f.write(line)


def remove_line_in_file(file: str, line: str) -> None:
    """Search line in file and remove it if found"""
    f = open(file, 'r')
    lines = f.readlines()
    f.close()

    f = open(file, 'w')
    for ln in lines:
        if ln != line:
            f.write(ln)
    f.close()


def remove(file: str) -> None:
    """Delete file ignoring FileNotFoundError"""
    try:
        os.remove(file)
    except FileNotFoundError:
        pass
