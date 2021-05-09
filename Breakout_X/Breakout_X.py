import pygame as pg
from pygame.locals import *
import random
import sys
from pathlib import Path
import numpy as np


FPS = 100
WINDOWWIDTH = 560
WINDOWHEIGHT = 700

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (66, 135, 245)
YELLOW = (255, 255, 0)

path_root = Path(__file__).parent

pg.init()
FPSCLOCK = pg.time.Clock()
DISPLAYSURF = pg.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))


class Ball(pg.sprite.Sprite):  # need to implement image, rect, update
    image = pg.transform.scale(
        pg.image.load(path_root / 'ball.png'), (14, 14))
    
    def __init__(self, cx, cy):
        super().__init__()
        self.vx, self.vy = 0, 0
        self.rect = self.image.get_rect()
        self.rect.center = cx, cy
    def launch(self, theta):  # in degree
        theta = np.deg2rad(theta) 
        self.vx, self.vy = 3*np.cos(theta), -3*np.sin(theta)
    def bounce_off(self, blocks):
        rect = self.rect
        for block in blocks:  # at most 2
            brect = block.rect
            if brect.top <= rect.centery < brect.bottom: self.vx = -self.vx
            if brect.left <= rect.centerx < brect.right: self.vy = -self.vy
    def update(self):
        cx, cy = self.rect.center
        cx += self.vx
        cy += self.vy
        if not 0 <= cx < WINDOWWIDTH: self.vx = -self.vx
        if not 0 <= cy < WINDOWHEIGHT: self.vy = -self.vy
        self.rect.center = cx, cy


class Block(pg.sprite.Sprite):
    font = pg.font.Font('Menlo-Regular.ttf', 16)

    def __init__(self, x, y, w, h):
        super().__init__()
        # self.image.fill(BLACK)  # background of this sprite
        # self.image.set_colorkey(BLACK)  # set it to be transparent
        self.count = 100
        self.x, self.y, self.w, self.h = x, y, w, h
        self.draw()
    
    def draw(self):
        self.image = pg.Surface((self.w, self.h))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y

        self.text_surface = self.font.render(str(self.count), True, WHITE)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = self.w//2, self.h//2
        
        pg.draw.rect(self.image, BLUE, [0, 0, self.w, self.h])
        pg.draw.rect(self.image, WHITE, [0, 0, self.w, self.h], 1)
        self.image.blit(self.text_surface, self.text_rect)

    def update(self, hit_list=None):
        if self in hit_list:
            self.count -= 1
            self.draw()


balls = pg.sprite.RenderPlain(Ball(WINDOWWIDTH//2, WINDOWHEIGHT-8))
blocks = pg.sprite.RenderPlain([Block(70*i, 0, 70, 42) for i in range(8)])
for ball in balls:
    ball.launch(30)

while True:
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()

    balls.update()
    for ball in balls:
        collisions = pg.sprite.spritecollide(ball, blocks, False)
        blocks.update(collisions)
        ball.bounce_off(collisions)

    DISPLAYSURF.fill(WHITE)
    balls.draw(DISPLAYSURF)
    blocks.draw(DISPLAYSURF)
    pg.display.flip()
    FPSCLOCK.tick(FPS)
