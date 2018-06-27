import time
import random


class Button:

    def __init__(self, code, in_address, out_address):
        self.code = code
        self.in_address = in_address
        self.out_address = out_address

    def turnon(self, seconds=0):
        # turn button light on using out_address, wait number of seconds
        time.sleep(seconds)

    def turnoff(self, seconds=0):
        # turn button light off using out_address, wait number of seconds
        time.sleep(seconds)

    def isPressed(self):
        # check in_address for whether button is currently being pressed
        return


class Simon:

    red = Button('r', 0, 0)
    yellow = Button('y', 0, 0)
    green = Button('g', 0, 0)
    blue = Button('b', 0, 0)

    buttons = {'r': red, 'y': yellow, 'g': green, 'b': blue}

    score = 0
    button_seq = random.choice('rgby')
    button_cur = button_seq[0]
    button_place = 0

    def blink(self, button, time_on=1, time_off=0.2):
        button.turnon(time_on)
        button.turnoff(time_off)

    def blink_all(self, time_on=1, time_off=0.2):
        for button in self.buttons.values:
            button.turnon(0)
        time.sleep(time_on)
        for button in self.buttons.values:
            button.turnoff(0)
        time.sleep(time_off)

    def fail_game(self):

        self.score = 0
        self.button_seq = random.choice('rgby')
        self.button_cur = self.button_seq[0]
        self.button_place = 0

        self.blink_all()
        self.blink_all()

        self.game_loop()

    def advance_color(self):

        if self.button_place + 1 == len(self.button_seq):
            # sequence completed, add next color and restart from beginning
            self.button_seq += random.choice('rgby')
            self.button_place = 0
            self.score += 1
            self.button_cur = self.button_seq[0]
            self.game_loop()
        else:
            self.button_place += 1
            self.button_cur = self.button_seq[self.button_place]

    def get_button_press(self):
        code = None
        for button in self.buttons.values:
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
        for button in self.buttons.values:
            button.turnon(seconds=1)
        for button in self.buttons.values:
            button.turnoff(seconds=0)
        self.game_loop()


game = Simon()
game.game_start()
