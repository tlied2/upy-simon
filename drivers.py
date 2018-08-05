''' Drivers for Simon game'''

import machine
import utime as time


class LEDBTN(object):
    ''' LED Button driver using mcp23008 '''

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
        self.bus = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))

        # Enable outputs, bits 4-7
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_IODIR, 0b00001111]))

        # Revese Polarity, bits 0-3
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_IPOL, 0b00001111]))

        # Enable pullups, bits 0-3
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPPU, 0b00001111]))

        # Turn off all lights
        self.all_off()

    def all_off(self):
        ''' Turns all lights off '''

        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPIO, 0x0]))

    def all_on(self):
        ''' Turns all lights on '''

        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPIO, 0xF0]))

    def light_on(self, code):
        ''' Turns on a single light '''

        print("Called lighton for %s" % code)
        val = self.bus.readfrom_mem(self.BASE_ADDR, self.MCP23008_GPIO, 1)[0] & 0xF0
        print("Orig Value: %s" % hex(val))
        newval = val | self.buttondict[code] << 4
        print("New Value: %s" % hex(newval))
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPIO, newval]))

    def light_off(self, code):
        ''' Turns off a single light '''

        print("Called lightoff for %s" % code)
        val = self.bus.readfrom_mem(self.BASE_ADDR, self.MCP23008_GPIO, 1)[0] & 0xF0
        print("Orig Value: %s" % hex(val))
        newval = val ^ self.buttondict[code] << 4
        print("New Value: %s" % hex(newval))
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPIO, newval]))

    def get_pressed(self):
        ''' Returns pressed button after it is released '''

        print("Waiting for button press")
        while True:
            val = self.bus.readfrom_mem(self.BASE_ADDR, self.MCP23008_GPIO, 1)[0] & 0x0F
            if val != 0:
                print("Button read val: %s" % hex(val))
                break

        print("Waiting for button release")
        while self.bus.readfrom_mem(self.BASE_ADDR, self.MCP23008_GPIO, 1)[0] & 0x0F == val:
            time.sleep(0.1)

        for key in self.buttondict:
            if val == self.buttondict[key]:
                return key
        print("This should never happen")
        return False
