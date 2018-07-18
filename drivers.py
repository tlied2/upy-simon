import machine


class driver:

    def __init__(self):
        self.bus = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))

        self.BASE_ADDR = 0x20

        self.MCP23008_IODIR = 0x00
        self.MCP23008_IPOL = 0x01
        self.MCP23008_GPINTEN = 0x02
        self.MCP23008_DEFVAL = 0x03
        self.MCP23008_INTCON = 0x04
        self.MCP23008_IOCON = 0x05
        self.MCP23008_GPPU = 0x06
        self.MCP23008_INTF = 0x07
        self.MCP23008_INTCAP = 0x08
        self.MCP23008_GPIO = 0x09
        self.MCP23008_OLAT = 0x0A

        # Enable outputs, bits 4-7
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_IODIR, 0b00001111]))

        # Revese Polarity, bits 0-3
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_IPOL, 0b00001111]))

        # Enable pullups, bits 0-3
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPPU, 0b00001111]))

        self.buttondict = {'r': (0b00001000, 0b10000000),
                           'y': (0b00000100, 0b01000000),
                           'g': (0b00000010, 0b00100000),
                           'b': (0b00000001, 0b00010000)}

    def lighton(self, code):
        val = self.bus.readfrom_mem(self.BASE_ADDR, self.MCP23008_GPIO, 1)[0] & 0x0F
        newval = val << 4 & self.buttondict(code)(1)
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPIO, newval]))

    def lightoff(self, code):
        val = self.bus.readfrom_mem(self.BASE_ADDR, self.MCP23008_GPIO, 1)[0] & 0x0F
        newval = (val << 4 ^ self.buttondict(code)(1))
        self.bus.writeto(self.BASE_ADDR, bytearray([self.MCP23008_GPIO, newval]))

    def getpressed(self, code):
        val = self.bus.readfrom_mem(self.BASE_ADDR, self.MCP23008_GPIO, 1)[0] & 0x0F
        if val & self.buttondict(code)(0) == val:
            return True
        return False
