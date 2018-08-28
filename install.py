''' Setup script to disable AP, configure STA, and install packages '''

import gc
import network
from utime import sleep
from upip import install

WIFI_CONFIG = ('SSID', 'PASSWORD')


def disable_ap():
    ''' Disable AP if enabled '''
    ap_if = network.WLAN(network.AP_IF)
    if ap_if.active():
        ap_if.active(False)


def init_wifi():
    ''' Enable client wifi for upip '''
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(*WIFI_CONFIG)

    print("Sleeping for WLAN")
    while not sta_if.isconnected():
        sleep(1)

print("Configuring Network")
disable_ap()
init_wifi()

print("Installing Packages")
gc.collect()
install([
    'micropython-logging',
    'micropython-uasyncio.queues',
    ], '/')
