import network
from utime import sleep
import gc
from upip import install

WIFI_CONFIG=('SSID', 'PASSWORD')
gc.collect()

def disable_ap():
    ''' Disable AP if enabled '''
    AP_IF = network.WLAN(network.AP_IF)
    if AP_IF.active():
        AP_IF.active(False)

def init_wifi():
    ''' Enable client wifi for upip '''
    STA_IF = network.WLAN(network.STA_IF)
    STA_IF.active(True)
    STA_IF.connect(*WIFI_CONFIG)

    print("Sleeping for WLAN")
    while not STA_IF.isconnected():
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
