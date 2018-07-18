import pygame as pg
from pygame.locals import *


FPS = 30  # 초당 프레임 수지만 사실상 게임속도
WINDOWWIDTH = 500
WINDOWHEIGHT = 700

BLOCKSIZE = 10


class Block(pg.sprite.Sprite):

    def __init__(self, color):

        super().__init__(self)
        self.image = pg.Surface((BLOCKSIZE, BLOCKSIZE))
        self.image.fill(color)  # todo : 나중에 더 이쁘게 칠해주기
        self.rect = self.image.get_rect()  # 여기까지 고정

        self.direction = [
            (0, -BLOCKSIZE),  # up
            (0, BLOCKSIZE),   # down
            (-BLOCKSIZE, 0),  # left
            (BLOCKSIZE, 0)    # right
        ]

    def move(self, x, y):
        self.rect.x, self.rect.y = x, y

    def move_ip(self, direction):
        self.rect.move_ip(self.direction[direction])


class Tetriminos:

    def __init__(self, color):
        self.blocks = [Block(color) for _ in range(4)]
        self.rotate = None

    def move(self, direction):
        pass


