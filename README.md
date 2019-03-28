# prime-switcher

Tool (GUI  + CLI) to select used GPU for Optimus Laptop on GNU/Linux.

## Supported Configurations

| Integrated GPU brand | Discrete GPU brand | Driver for discrete GPU | Supported |
|----------------------|--------------------|-------------------------|-----------|
| Intel                | NVIDIA             | nvidia (Proprietary)    | Yes       |
| Intel                | NVIDIA             | nouveau                 | Yes       |
| Intel or AMD         | AMD                | amdgpu-pro (Proprietary)| No        |
| Intel or AMD         | AMD                | amdgpu, radeon          | Yes       |

## Dependencies

- Python 3.7
- python-gobject
- gtk3
- libappindicator-gtk3
- libnotify
- mesa-utils (glxinfo)
- bbswitch (Optional but recommended for power-saving with NVIDIA discrete GPU)

## How to install 

**Warning : You must install drivers for discrete GPU before installing the switcher**

### Arch Linux/Manjaro

AUR Package : https://aur.archlinux.org/packages/prime-switcher/

### Other Distribution

```bash
# ./install.sh
```

## How to use


### Select GPU to use

```bash
# prime-switcher -s {mode}
```

Modes :
- performance : Use the discrete GPU as primary GPU.
- power-saving : Disable the discrete GPU if possible.


### Select target driver

#### Automatic detection

```bash
# prime-switcher -D -s {mode}
```

#### Manual selection
```bash
# prime-switcher -d {driver} -s {mode}
```

Drivers :
- free : Free drivers (amdgpu, radeon, nouveau without bbswitch)
- nvidia : NVIDIA proprietary driver
- nouveau : nouveau driver
- nvidia-reverse-prime : NVIDIA proprietary driver with Reverse Prime (Discrete GPU managing some output ports)
- nouveau-reverse-prime : nouveau driver with Reverse Prime

### Get current used GPU
```bash
prime-switcher -q
```

### Open GUI
```bash
prime-switcher --gui
```

### Remove patches applied by the switcher
```bash
# prime-switcher --uninstall
```