import subprocess
import os


def execute_command(cmd) -> str:
    return subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().decode()


def get_config_filepath(file: str) -> str:
    return os.path.join('/etc/prime-switcher/', file)


def replace_in_file(file: str, text: str, replace: str):
    f = open(file, 'r')
    file_data = f.read()
    f.close()

    new_data = file_data.replace(text, replace)

    f = open(file, 'w')
    f.write(new_data)
    f.close()


def create_symlink(source: str, dest: str):
    if os.path.exists(dest):
        os.remove(dest)
    os.symlink(source, dest)


def file_contains(file: str, text: str) -> bool:
    with open(file, 'r') as f:
        data = f.read()
        return text in data


def write_line_in_file(file: str, line: str):
    with open(file, 'a') as f:
        f.write(line)


def remove_line_in_file(file: str, line: str):
    f = open(file, 'r')
    lines = f.readlines()
    f.close()

    f = open(file, 'w')
    for ln in lines:
        if ln != line:
            f.write(ln)
    f.close()
