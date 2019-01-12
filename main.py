import pygame as pg
import traceback
from game_states import Game


if __name__ == '__main__':
    try:
        g = Game()
        g.run()
    except:
        traceback.print_exc()
        pg.quit()