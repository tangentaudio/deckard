# Intro

```
   __| | ___  ___| | ____ _ _ __ __| |
  / _` |/ _ \/ __| |/ / _` | '__/ _` |
 | (_| |  __/ (__|   < (_| | | | (_| |
  \__,_|\___|\___|_|\_\__,_|_|  \__,_|
```

Deckard provides StreamDeck support for LinuxCNC, allowing deck buttons to reflect and control HAL pins.  This allows creating responsive, tactile user interfaces for LinuxCNC machines.

## How to install and use

Clone this repository.  It is assumed you clone it into your home directory, e.g. `~/deckard`

### Configure Prerequisites

- Ensure system is up to date, upgrade all out of date packages: `sudo apt update && sudo apt dist-upgrade -y`
- Install the pip Python package manager: `sudo apt install -y python3-pip python3-setuptools`
- Install system packages needed for the default LibUSB HIDAPI backend: `sudo apt install -y libudev-dev libusb-1.0-0-dev libhidapi-libusb0`
- Install system packages needed for the Python Pillow package installation: `sudo apt install -y libjpeg-dev zlib1g-dev libopenjp2-7`
- Add udev rule to allow all users non-root access to StreamDeck devices:
```
sudo tee /etc/udev/rules.d/10-streamdeck.rules << EOF
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0fd9", GROUP="users", TAG+="uaccess"
EOF
```
- Reload udev rules to ensure the new permissions take effect: `sudo udevadm control --reload-rules`
- Unplug and replug your StreamDeck device.

### Set up Python virtual environment

To avoid polluting the system python installation, you need to set up a python virtual environment.

- `cd ~/deckard`
- Set up a python virtual environment: `python3 -m venv .venv --system-site-packages`
- Install the pillow library: `.venv/bin/pip3 install pillow`
- Install the StreamDeck python library: `.venv/bin/pip3 install streamdeck`

### Run an example

Bundled is a `sim.axis` configuration with a few basic functions connected to Deckard. This demo is built for a 32-button StreamDeck; to use a smaller one you will need to modify the example.

Plug in a StreamDeck into your LinuxCNC PC and run the following.

`PATH=$PATH:~/deckard linuxcnc ~/deckard/example/deckard.sim/axis.ini`

