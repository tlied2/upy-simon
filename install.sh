#!/bin/sh

SER=/dev/ttyUSB0
AMPY="ampy -p ${SER}"

#${AMPY} mkdir lib
${AMPY} run install.py

./update.sh
