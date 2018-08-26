''' Drivers for Simon game'''

from machine import Pin, Signal, I2C, Timer
import utime as time

# Global for interrupt signalling
#button_pressed = False


#def int_callback(pin):
    #global button_pressed
    #button_pressed = True
    #print("Interrupt callback: ", pin)


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
        self.bus = I2C(scl=Pin(self.SCL), sda=Pin(self.SDA))
        self.int = Signal(self.INT, Pin.IN, Pin.PULL_UP, invert=True)
        #self.int = Pin(self.INT, Pin.IN, Pin.PULL_UP)
        self.timer = Timer(-1)

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

        # Register Interrupt for Button Presses
        #self.int.irq(trigger=Pin.IRQ_FALLING, handler=int_callback)

    def all_off(self):
        ''' Turns all lights off '''

        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPIO, 0x0]))

    def all_on(self):
        ''' Turns all lights on '''

        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPIO, 0xF0]))

    def blink(self, color, time_on):
        ''' Blink an LED for a specified time, but return immediately '''
        print("Blinking Value: %s" % hex(self.buttondict[color] << 4))
        self.bus.writeto(
            self.BASE_ADDR,
            bytearray([self.MCP23008_GPIO, self.buttondict[color] << 4]))
        print("Setting timer: ", int(time_on * 1000), "ms")
        self.timer.init(
            period=int(time_on * 1000),
            mode=Timer.ONE_SHOT,
            callback=lambda t: self.light_off(color))

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
        #global button_pressed

        # Interrupt already waiting, read until clear
        while self.int.value():
            print("Clearing existing interrupt")
            val = self.bus.readfrom_mem(self.BASE_ADDR, self.MCP23008_INTCAP, 1)[0] & 0x0F
            print("Button read val: %s" % hex(val))
            #button_pressed = False

        # Stall until interrupt fires
        #while not button_pressed:
        while not self.int.value():
            time.sleep(0.1)

        # Read value that caused interrupt
        val = self.bus.readfrom_mem(self.BASE_ADDR, self.MCP23008_INTCAP, 1)[0] & 0x0F
        #button_pressed = False

        print("Button read val: %s" % hex(val))

        for key in self.buttondict:
            if val == self.buttondict[key]:
                return key
        print("This should never happen")
        return False
