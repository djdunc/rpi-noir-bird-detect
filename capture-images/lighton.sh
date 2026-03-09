#!/bin/bash

# first off turn on the IR LEDs'
#   Exports pin to userspace
sudo echo "4" > /sys/class/gpio/export  

# Sets pin 4 as an output
sudo echo "out" > /sys/class/gpio/gpio4/direction

# Sets pin 4 to high
sudo echo "1" > /sys/class/gpio/gpio4/value
