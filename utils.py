import subprocess
import os
import re


def execute_command(cmd) -> str:
    return subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().decode()


def get_config_filepath(file: str) -> str:
    return os.path.join('/etc/prime-switcher/', file)


def get_gpu_brand_list() -> list:
    data = execute_command('lspci').lower()
    reg = re.compile(r'(vga|display|hdmi|3d)')
    list = []
    for device in data.split('\n'):
        if reg.search(device):
            result = re.search(r'.*:\s*([^ ]*)', device)
            if result:
                list.append(result.group(1))
    return list


def replace_in_file(file: str, text: str, replace: str) -> None:
    f = open(file, 'r')
    file_data = f.read()
    f.close()

    new_data = file_data.replace(text, replace)

    f = open(file, 'w')
    f.write(new_data)
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
