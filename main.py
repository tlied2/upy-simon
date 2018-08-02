import machine
import time
import urandom
import drivers

driver = drivers.driver()


def pick_item(sequence):
    div = 0x3fffffff // len(sequence)
    return sequence[urandom.getrandbits(30) // div]


class Button:

    def __init__(self, code):
        self.code = code

    def turnon(self, seconds=0):
        driver.lighton(self.code)
        time.sleep(seconds)

    def turnoff(self, seconds=0):
        driver.lightoff(self.code)
        time.sleep(seconds)

    def isPressed(self):
        driver.getpressed(self.code)
        return


class Simon:

    def __init__(self):
        self.red = Button('r')
        self.yellow = Button('y')
        self.green = Button('g')
        self.blue = Button('b')

        self.buttons = {'r': self.red, 'y': self.yellow, 'g': self.green, 'b': self.blue}

        self.score = 0
        self.button_seq = pick_item('rgby')
        self.button_cur = self.button_seq[0]
        self.button_place = 0

    def blink(self, button, time_on=1, time_off=0.2):
        button.turnon(time_on)
        button.turnoff(time_off)

    def blink_all(self, time_on=1, time_off=0.2):
        for button in self.buttons.values():
            button.turnon(0)
        time.sleep(time_on)
        for button in self.buttons.values():
            button.turnoff(0)
        time.sleep(time_off)

    def fail_game(self):

        self.score = 0
        self.button_seq = pick_item('rgby')
        self.button_cur = self.button_seq[0]
        self.button_place = 0

        self.blink_all()
        self.blink_all()

        self.game_loop()

    def advance_color(self):

        if self.button_place + 1 == len(self.button_seq):
            # sequence completed, add next color and restart from beginning
            self.button_seq += pick_item('rgby')
            self.button_place = 0
            self.score += 1
            self.button_cur = self.button_seq[0]
            self.game_loop()
        else:
            self.button_place += 1
            self.button_cur = self.button_seq[self.button_place]

    def get_button_press(self):
        code = None
        for button in self.buttons.values():
            if button.isPressed():
                code = button.code
        return code

    def game_loop(self):

        time.sleep(1)
        self.do_sequence()

        while True:

            code = self.get_button_press()
            if code is not None:
                if code == self.button_cur:
                    while self.buttons[code].isPressed():
                        time.sleep(0.1)
                    self.advance_color()
                    self.blink(self.buttons[code], 0.5, 0)
                else:
                    while self.buttons[code].isPressed():
                        time.sleep(0.1)
                    self.fail_game()

    def do_sequence(self):

        for color in self.button_seq:
            self.blink(self.buttons[color])

    def game_start(self):
        for button in self.buttons.values():
            button.turnon(seconds=1)
        for button in self.buttons.values():
            button.turnoff(seconds=0)
        self.game_loop()


game = Simon()
print('game start')
game.game_start()
