#!/bin/sh

SER=/dev/ttyUSB0
AMPY="ampy -p ${SER}"

${AMPY} put src/drivers.py
${AMPY} put src/main.py
