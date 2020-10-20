# Capstone Project
This is the Capstone project for Team 7 at The Ohio State University Department of Electrical and Computer Engineering

# Software
This project uses the ESP32 port of Micropython. The most recent firmware versions for the ESP32 are located in the root level of the repository.

## Getting started
To get started developing with Micropython for this project, the following steps are required:
1. Install [Python](https://www.python.org/downloads/), if not already installed
2. Use pip to install [esptool](https://pypi.org/project/esptool/) and [adafruit-ampy](https://pypi.org/project/adafruit-ampy/)
3. Ensure the `make` utility is installed (for Windows users, see WSL)

The following tools are recommended:
1. [VS Code](https://code.visualstudio.com), with the python extension installed
2. A serial port monitor, such as the one included with the [Arduino IDE](https://www.arduino.cc/en/Main/Software), the GNU utility `screen`, or the terminal emulator program [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)
3. The [micropy-cli](https://pypi.org/project/micropy-cli/) tool to generate stubs for code completion in VS Code

### Flashing the firmware
To flash the firmware, run `make flash` in the root directory of the repository. This will flash the provided micropython firmware for the ESP32. There are two versions of the firmware, one compiled with the version 3 of the ESP-IDF toolchain and one compiled with version 4. The default option flashes the version 4 variant of the firmware.

This process can take a while.

### Working with micropython files on the ESP32
The below table shows the commands that can be run using the makefile to work with files on the ESP32.

Command | Arguments | Description | Example
------- | --------- | ----------- | -------
`make list` | `port` | Lists the files currently on the ESP32 | `make list port=/dev/tty.usbserial-14120`
`make put` | `port`, `file` | Loads a file from the local filesystem to the ESP32's internal filesystem | `make put port=/dev/tty.usbserial-14120 file=software/src/boot.py`
`make show` | `port`, `file` | Gets and prints out the contents of a file currently on the ESP32 | `make show port=/dev/tty.usbserial-14120 file=main.py`
`make reset` | `port` | Performs a hard reset of the ESP32 | `make reset port=/dev/tty.usbserial-14120`

To get a running demo of the latest code in the repository, each of the files in the [software/src](https://github.com/gworkman/capstone-ece4900/tree/master/software/src) directory should be loaded using the `make put` command shown above. Note that for windows users, the port will be the COM port where the ESP32 is mounted.

# Hardware
This project includes a custom-designed add-on board for the ESP32 to mount a variety of sensors in a small package.

## Getting started
If you just want to purchase the board, you can use the gerber files in the hardware/output directory to do so at your favorite PCB fab house. A bill of materials and PDF of the schematic is also included in the hardware/output directory for reference.
To make changes to the design of the board, you will need KiCad, a free PCB design software. Just open the `hardware.pro` file in KiCad, then you are good to start making changes.
