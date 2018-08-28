''' Simon game implementation '''

import logging
import urandom
import utime as time
import uasyncio as asyncio

from drivers import LEDBTN

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
#asyncio.set_debug(True)
#asyncio.core.set_debug(True)


class Simon(object):
    ''' Main Simon game object '''

    buttons = ['r', 'y', 'g', 'b']

    def __init__(self, driver):
        self.driver = driver
        self.failed = True
        self.score = 0
        self.button_seq = []

    def pick_color(self):
        ''' Returns a random color '''
        div = 0x3fffffff // len(self.buttons)
        return self.buttons[urandom.getrandbits(30) // div]

    async def fail_game(self):
        ''' Wrong button pressed, clear everything and flash lights '''
        self.score = 0
        self.button_seq = []
        self.failed = True

        for idx in range(3):
            await self.driver.blink_all()

    async def game_loop(self):
        ''' Main game loop '''
        log.info('Game Start')
        while not self.failed:
            log.info("Playing game, score: %d", self.score)
            await asyncio.sleep(2)

            self.button_seq += self.pick_color()
            await self.do_sequence()

            for color in self.button_seq:
                try:
                    gotcolor = await asyncio.wait_for(self.driver.get_pressed(), 5)
                except asyncio.TimeoutError:
                    log.info("Timed out waiting for button press")
                    gotcolor = None

                if gotcolor == color:
                    await self.driver.blink(color, 0.5)

                else:
                    await self.fail_game()
                    self.failed = True
                    break

            self.score += 1

    async def main_loop(self):
        ''' Endless loop to play games '''

        while True:
            await self.welcome()

            log.info("Waiting for keypress to start game")
            await self.driver.get_pressed()
            await self.welcome(0.25)

            urandom.seed(time.ticks_cpu())
            self.failed = False
            await self.game_loop()

    async def do_sequence(self):
        ''' Displays current color sequence '''
        self.driver.all_off()
        await asyncio.sleep(0.5)
        for color in self.button_seq:
            print("Do sequence, color: %s" % color)
            await self.driver.blink(color, 1)
            await asyncio.sleep(0.2)

    async def welcome(self, delay=1):
        ''' Welcome light show '''
        log.info('Welcome Lights')
        for button in self.buttons:
            self.driver.light_on(button)
            await asyncio.sleep(delay)
        self.driver.all_off()


def main():
    ''' Main entry point '''

    driver = LEDBTN()
    game = Simon(driver)

    loop = asyncio.get_event_loop()
    log.info("Create game task")
    loop.create_task(driver.read_buttons())
    loop.create_task(game.main_loop())
    log.info("Running forever")
    loop.run_forever()


main()
