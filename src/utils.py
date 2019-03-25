import subprocess
import os
import re
import gpu
from typing import List
from typing import Dict


def execute_command(cmd) -> str:
    return subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().decode()


def get_debug_folder(path: str) -> str:
    return os.path.join(os.path.dirname(os.getcwd()), path)


def get_config_filepath(file: str) -> str:
    return os.path.join(get_debug_folder('configs') if os.getenv('DEBUG', 0) else '/etc/prime-switcher/', file)


def get_gpu_list() -> List[gpu.GPU]:
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
    if os.path.exists(dest):
        os.remove(dest)
    os.symlink(source, dest)


def file_contains(file: str, text: str) -> bool:
    with open(file, 'r') as f:
        data = f.read()
        return text in data


def write_line_in_file(file: str, line: str) -> None:
    with open(file, 'a') as f:
        f.write(line)


def remove_line_in_file(file: str, line: str) -> None:
    f = open(file, 'r')
    lines = f.readlines()
    f.close()

    f = open(file, 'w')
    for ln in lines:
        if ln != line:
            f.write(ln)
    f.close()


def remove(file: str) -> None:
    try:
        os.remove(file)
    except FileNotFoundError:
        pass
