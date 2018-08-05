''' Simon game implementation '''

import utime as time
import urandom

from drivers import LEDBTN


class Simon(object):
    ''' Main Simon game object '''

    buttons = ['r', 'y', 'g', 'b']

    def __init__(self, driver):
        self.driver = driver
        self.score = 0
        self.button_seq = []

    def pick_color(self):
        ''' Returns a random color '''
        div = 0x3fffffff // len(self.buttons)
        return self.buttons[urandom.getrandbits(30) // div]

    def blink(self, color, time_on=1, time_off=0.2):
        ''' Blink light identified by color with timings specified '''
        self.driver.light_on(color)
        time.sleep(time_on)
        self.driver.light_off(color)
        time.sleep(time_off)

    def blink_all(self, time_on=1, time_off=0.2):
        ''' Blink all lights with timings specified '''
        self.driver.all_on()
        time.sleep(time_on)
        self.driver.all_off()
        time.sleep(time_off)

    def fail_game(self):
        ''' Wrong button pressed, clear everything and flash lights '''
        self.score = 0
        self.button_seq = []

        for idx in range(3):
            self.blink_all()

    def game_loop(self):
        ''' Main game loop '''
        failed = False

        while not failed:
            time.sleep(2)

            self.button_seq += self.pick_color()
            self.do_sequence()

            for color in self.button_seq:
                gotcolor = self.driver.get_pressed()

                if gotcolor == color:
                    self.blink(color, 0.5, 0)
                else:
                    self.fail_game()
                    failed = True
                    break

    def do_sequence(self):
        ''' Displays current color sequence '''
        for color in self.button_seq:
            print("Do sequence, color: %s" % color)
            self.blink(color)

    def welcome(self):
        ''' Welcome light show '''
        for button in self.buttons:
            self.driver.light_on(button)
            time.sleep(1)
        self.driver.all_off()


def main():
    ''' Main entry point '''
    driver = LEDBTN()
    game = Simon(driver)

    print('Welcome Lights')
    game.welcome()

    while True:
        # Wait for keypress to start game
        driver.get_pressed()

        print('Game Start')
        game.game_loop()
        print("Game finished, starting new game")


if __name__ == '__main__':
    main()
