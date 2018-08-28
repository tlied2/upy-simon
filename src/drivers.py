''' Drivers for Simon game'''

from machine import Pin, Signal, I2C
import uasyncio as asyncio
from uasyncio.queues import Queue

import logging
log = logging.getLogger(__name__)


class LEDBTN(object):
    ''' LED Button driver using mcp23008 '''

    SCL = 5
    SDA = 4
    INT = 2

    BASE_ADDR = 0x20

    MCP23008_IODIR = 0x00
    MCP23008_IPOL = 0x01
    MCP23008_GPINTEN = 0x02
    MCP23008_DEFVAL = 0x03
    MCP23008_INTCON = 0x04
    MCP23008_IOCON = 0x05
    MCP23008_GPPU = 0x06
    MCP23008_INTF = 0x07
    MCP23008_INTCAP = 0x08
    MCP23008_GPIO = 0x09
    MCP23008_OLAT = 0x0A

    buttondict = {'b': 0b00001000,
                  'g': 0b00000100,
                  'y': 0b00000010,
                  'r': 0b00000001}

    def __init__(self):
        log.info("MCP23008 Initializing")
        self.bus = I2C(scl=Pin(self.SCL), sda=Pin(self.SDA))
        self.int = Signal(self.INT, Pin.IN, Pin.PULL_UP, invert=True)
        self.input = Queue(10)

        # Enable outputs, bits 4-7
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_IODIR, 0b00001111]))

        # Reverse Polarity, bits 0-3
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_IPOL, 0b00001111]))

        # Enable pullups, bits 0-3
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPPU, 0b00001111]))

        # Set interrupt to open-drain
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_IOCON, 0b00000100]))

        # Compare against DEFVAL
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_INTCON, 0b00001111]))

        # Enable Interrupt on Change
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPINTEN, 0b00001111]))

        # Turn off all lights
        self.all_off()

    def all_off(self):
        ''' Turns all lights off '''
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPIO, 0x0]))

    def all_on(self):
        ''' Turns all lights on '''
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPIO, 0xF0]))

    async def blink(self, color, time_on):
        ''' Blink an LED for a specified time, but return immediately '''
        log.info("Blinking Value: %s" % hex(self.buttondict[color] << 4))
        self.bus.writeto(
            self.BASE_ADDR,
            bytearray([self.MCP23008_GPIO, self.buttondict[color] << 4]))
        await asyncio.sleep(time_on)
        self.light_off(color)

    async def blink_all(self, time_on=1, time_off=0.2):
        ''' Blink all lights with timings specified '''
        log.info("Blink all lights")
        self.all_on()
        await asyncio.sleep(time_on)
        self.all_off()
        await asyncio.sleep(time_off)

    def light_on(self, code):
        ''' Turns on a single light '''
        log.info("Called lighton for %s" % code)

        val = self.bus.readfrom_mem(self.BASE_ADDR, self.MCP23008_GPIO, 1)[0] & 0xF0
        log.debug("Orig Value: %s" % hex(val))
        newval = val | self.buttondict[code] << 4
        log.debug("New Value: %s" % hex(newval))
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPIO, newval]))

    def light_off(self, code):
        ''' Turns off a single light '''
        log.info("Called lightoff for %s" % code)

        val = self.bus.readfrom_mem(self.BASE_ADDR, self.MCP23008_GPIO, 1)[0] & 0xF0
        log.debug("Orig Value: %s" % hex(val))
        newval = val ^ self.buttondict[code] << 4
        log.debug("New Value: %s" % hex(newval))
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPIO, newval]))

    def lookup_key(self, val):
        ''' Return letter color code for a button press value
            TODO: Fix this, it seems silly to iterate '''
        for key in self.buttondict:
            if val == self.buttondict[key]:
                return key
        log.error("Unknown key: %s", hex(val))
        return False

    async def read_buttons(self):
        ''' Read button presses and add them to self.input Queue '''
        while True:
            if self.int.value():
                log.debug("Button interrupt high")
                val = self.bus.readfrom_mem(self.BASE_ADDR, self.MCP23008_INTCAP, 1)[0] & 0x0F
                log.debug("Adding %s to queue" % val)
                await self.input.put(self.lookup_key(val))
                log.debug("Added %s to queue" % val)
                # Debounce delay
                await asyncio.sleep(0.1)
                # Clear bounces
                while self.int.value():
                    val = self.bus.readfrom_mem(self.BASE_ADDR, self.MCP23008_INTCAP, 1)[0] & 0x0F
            else:
                await asyncio.sleep(0.1)

    async def get_pressed(self):
        ''' Returns pressed button after it is released '''
        log.info("Waiting for button press")

        # Just wait for the queue to have data
        val = await self.input.get()
        return val
