# Intro

![deckard](assets/deckard.png)

Deckard provides StreamDeck support for LinuxCNC, allowing deck buttons to reflect and control HAL pins.  This allows creating responsive, tactile user interfaces for LinuxCNC machines.

[Origin of the project name](https://en.wikipedia.org/wiki/Rick_Deckard)

## Versions

This was built for LinuxCNC 2.9.2 from the standard Debian 12 ISO image.  It probably will work on other versions, but you're in somewhat uncharted waters.

## Installation

Start by cloning this repository.  It is assumed you clone it into your home directory, e.g. `~/deckard`

### Configure Prerequisites

- Ensure system is up to date, upgrade all out of date packages: `sudo apt update`
- Install pip: `sudo apt install -y python3-pip python3-setuptools`
- Install venv: `sudo apt install python3-venv`
- Install libusb stuff: `sudo apt install -y libudev-dev libusb-1.0-0-dev libhidapi-libusb0`
- Install Python Pillow prereqs: `sudo apt install -y libjpeg-dev zlib1g-dev libopenjp2-7`
- Add udev rule to allow all users non-root access to StreamDeck devices as follows:
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
- Install pynput: `.venv/bin/pip3 install pynput`

### Run a basic example in `halrun`

A simple demo using a minimal hal file and a small Deckard config file is available in the `examples` directory.

To run it:

- Switch to the examples directory: `cd ~/deckard/examples`
- Run the script: `./runsimple.sh`

If it's all working, you should see a few buttons light up on your StreamDeck, and output on the console similar to this:

```
steve@bcm-linuxcnc:~/deckard/example$ ./runexample.sh 
Note: Using POSIX realtime
Deckard found 1 deck(s).

Opened 'Stream Deck XL' device (serial number: 'CL07L2A00458', fw: '1.01.000')
Component Pins:
Owner   Type  Dir         Value  Name
    15  bit   IN          FALSE  deckard.0.02.in <== td0-out
    15  bit   OUT         FALSE  deckard.0.02.out ==> td0-in
    15  bit   IN          FALSE  deckard.0.ButtonOne.in <== t0-out
    15  bit   OUT         FALSE  deckard.0.ButtonOne.out ==> t0-in
    15  bit   IN          FALSE  deckard.0.ButtonTwo.in <== t1-out
    15  bit   OUT         FALSE  deckard.0.ButtonTwo.out ==> t1-in
     5  s32   OUT          1140  main-thread.time
    11  float OUT             0  timedelay.0.elapsed
    11  bit   IN          FALSE  timedelay.0.in <== td0-in
    11  float IN              2  timedelay.0.off-delay
    11  float IN            0.5  timedelay.0.on-delay
    11  bit   OUT         FALSE  timedelay.0.out ==> td0-out
    11  s32   OUT           152  timedelay.0.time
     8  bit   IN          FALSE  toggle.0.in <== t0-in
     8  bit   I/O         FALSE  toggle.0.out <=> t0-out
     8  s32   OUT           186  toggle.0.time
     8  bit   IN          FALSE  toggle.1.in <== t1-in
     8  bit   I/O         FALSE  toggle.1.out <=> t1-out
     8  s32   OUT            36  toggle.1.time

```

This demonstrates two toggle buttons implemented with the HAL `toggle` component, and a time-delay button implemented with the `timedelay` component.  You can type `exit` or hit Ctrl-D at the halcmd prompt to quit.

### Run a full LinuxCNC example

Bundled is a `sim.axis` configuration with a few basic functions connected to Deckard. NOTE; This demo is built for a 32-button StreamDeck; to use a smaller deck you will need to modify the example.

Plug in a StreamDeck into your LinuxCNC PC and run the sim:

- Switch to the examples directory: `cd ~/deckard/examples`
- Run the script: `./runaxis.sh`

You should see several buttons load on the StreamDeck, and a classic Axis GUI will launch on your desktop.  The demo shows real interaction with LinuxCNC HAL components, such as:

- E-Stop set/reset
- Machine power on/off
- Home All
- Cycle Start / Hold / Stop
- Axis Error Notifications / Clearing

## Deckard Configuration and Use

More info on configuration and use is contained in the GitHub wiki for this project.

