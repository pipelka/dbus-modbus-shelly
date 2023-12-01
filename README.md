# dbus-modbus-shelly

Integrate a Shelly Pro 3EM smart meter into [Victron Energies Venus OS](https://github.com/victronenergy/venus) via modbus.

## Install & Configuration

### Clone the repository

Get a copy of the master branch and put it to `/data/dbus-modbus-shelly`.
After that call the `install.sh` script.

```
cd /data
git clone https://github.com/pipelka/dbus-modbus-shelly.git
cd dbus-modbus-shelly
./install.sh
```

**_Note:_** you need to install the `git` utility on your device to be able to clone the repository:
```
opkg install git
```

### Install by script

Use the following script to setup everything automatically:
```
wget https://github.com/pipelka/dbus-modbus-shelly/archive/refs/heads/master.zip
unzip master.zip "dbus-modbus-shelly-master/*" -d /data
mv /data/dbus-modbus-shelly-master /data/dbus-modbus-shelly
chmod a+x /data/dbus-modbus-shelly/install.sh
/data/dbus-modbus-shelly/install.sh
rm master.zip
```

### Configuration

Your Shelly device will by detected and configured automagically.

## External Documentation

- [Shelly Gen2 Modbus Registers](https://shelly-api-docs.shelly.cloud/gen2/ComponentsAndServices/EM/#modbus-registers)
- [Customizing a GX device](https://www.victronenergy.com/live/ccgx:root_access#customizing_a_gx_device)

## References

This project is inspired by the following people and their work:
- https://github.com/victronenergy/dbus-modbus-client
- https://github.com/Jalle19/dbus-modbus-client/tree/shelly-pro3em
- https://github.com/fabian-lauer/dbus-shelly-3em-smartmeter

## Warning

This code may threaten your life, burn your Victron device, kill you and others, ...
you get the picture.
