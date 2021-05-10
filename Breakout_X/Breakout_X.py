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

LEFT = 1  # left mouse button
RIGHT = 3  # right

pg.init()
FPSCLOCK = pg.time.Clock()
DISPLAYSURF = pg.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
MAX_LINE = 16  # game over criteria
pg.display.set_caption('Breakout X By Haawron')

path_root = Path(__file__).parent


class Ball(pg.sprite.Sprite):  # need to implement image, rect, update
    image = pg.transform.scale(
        pg.image.load(path_root / 'ball.png'), (14, 14))
    
    def __init__(self, cx, cy):
        super().__init__()
        self.v0 = 5
        self.vx, self.vy = 0, 0
        self.rect = self.image.get_rect()
        self.rect.center = cx, cy
        self.pos_float = np.array(self.rect.topleft).astype(np.float64)
        self.stopped = True
    def __bool__(self):
        return self.stopped
    def move(self, offset_x, offset_y):
        """Since pygame always quantizes the position of rect,
        we need to keep track of exact position of rect"""
        self.pos_float += [offset_x, offset_y]
        self.rect.update(*self.pos_float, *self.rect.size)
    def launch(self, theta):  # theta in rad
        self.vx, self.vy = self.v0*np.cos(theta), -self.v0*np.sin(theta)
        self.stopped = False
    def bounce_off(self, blocks):
        convert_x, convert_y = False, False
        rect = self.rect
        for block in blocks:  # at most 2
            brect = block.rect
            # converting vx/vy in this loop could convert sign twice
            if rect.centerx < brect.left or rect.centerx > brect.right:
                convert_x = True
            if rect.centery < brect.top or rect.centery > brect.bottom:
                convert_y = True
        if convert_x:
            self.vx = -self.vx
            self.move(self.vx, 0)
        if convert_y:
            self.vy = -self.vy
            self.move(0, self.vy)
    def update(self):
        self.move(self.vx, self.vy)
        if self.rect.left <= 0 or self.rect.right >= WINDOWWIDTH:
            self.vx = -self.vx
            self.move(self.vx, 0)
        if self.rect.top <= 0:
            self.vy = -self.vy
            self.move(0, self.vy)
        elif self.rect.bottom >= WINDOWHEIGHT:
            self.stopped = True
            self.vx, self.vy = 0, 0
            self.rect.bottom = WINDOWHEIGHT-1
            self.pos_float = np.array(self.rect.topleft).astype(np.float64)


class Block(pg.sprite.Sprite):
    font = pg.font.Font('Menlo-Regular.ttf', 16)

    def __init__(self, x, y, w, h, count):
        super().__init__()
        self.count = count
        self.image = pg.Surface((w, h))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.w, self.h = w, h
        self.draw()

    def draw(self):
        self.image = pg.Surface((self.w, self.h))
        self.rect = self.image.get_rect(center=self.rect.center)
        self.text_surface = self.font.render(str(self.count), True, WHITE)
        self.text_rect = self.text_surface.get_rect()
        self.text_rect.center = self.w//2, self.h//2
        
        pg.draw.rect(self.image, BLUE, [0, 0, self.w, self.h])
        pg.draw.rect(self.image, WHITE, [0, 0, self.w, self.h], 1)
        self.image.blit(self.text_surface, self.text_rect)

    def update(self, hit_list=None):
        if self in hit_list:
            self.count -= 1
            global score
            score += 1
            if self.count == 0:
                print([block.rect.left for block in blocks])
                for group in self.groups():
                    group.remove(self)
                self.kill()
            else:
                self.draw()


def generate_blocks(p, count):
    return [
        Block(70*i, 0, 70, 42, random.randint(1, count)) 
        for i, x in enumerate(np.random.choice(2, 8, p=[p, 1-p])) if x]


def info_text(surface, text, fontsize, **rect_kwargs):
    font = pg.font.Font('Menlo-Regular.ttf', fontsize)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(**rect_kwargs)
    surface.blit(text_surface, text_rect)


score = 0
phase = 0
direction = 0
delay_count = 0  # frame delay between launches
balls_count = 0
collect_count = 0
balls_list = []
offsets = {}
launching = False
arrow_image = pg.transform.scale(pg.image.load(path_root / 'arrow.png'), (200, 30))
arrow_image.fill(WHITE, pg.Rect(0, 0, 100, 30))
arrow_image.set_colorkey(WHITE)

chief_ball = Ball(WINDOWWIDTH//2, WINDOWHEIGHT-8)
balls = pg.sprite.RenderPlain(chief_ball)
blocks = pg.sprite.RenderPlain(generate_blocks(.5, 5))

done = False

while not done:
    delta_t = FPSCLOCK.tick(FPS)
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()
        if event.type == MOUSEBUTTONUP and event.button == LEFT:
            launching = True

    if phase == 0:  # setting the direction to fire
        mousex, mousey = pg.mouse.get_pos()
        dx, dy = mousex-chief_ball.rect.center[0], mousey-chief_ball.rect.center[1]
        direction = np.clip(np.arctan2(-dy, dx), np.deg2rad(15), np.deg2rad(165))  # rad
        if launching:
            phase = 1
            balls_count = len(balls)
            balls_list = balls.sprites()
    elif phase == 1:  # launching and balls are moving
        if delay_count != 0:
            delay_count -= 1
        elif balls_count:  # if any ball is not launched
            balls_list[balls_count-1].launch(direction)
            delay_count = int(.03 * FPS)  # 30 ms in frame
            balls_count -= 1
        else:
            launching = False
            delay_count = 0
        balls.update()
        for ball in balls:
            collisions = pg.sprite.spritecollide(ball, blocks, False)
            blocks.update(collisions)
            ball.bounce_off(collisions)
        if all(balls):  # have stopped
            phase = 2
            collect_count = int(.3 * FPS)  # 300 ms
            offsets = {ball: (chief_ball.rect.centerx - ball.rect.centerx) / collect_count for ball in balls}
    elif phase == 2:  # collecting balls and moving/adding blocks
        if collect_count != 0:
            collect_count -= 1
            for ball in balls:
                ball.move(offsets[ball], 0)
        else:
            phase = 0
            for ball in balls:
                ball.rect.centerx = chief_ball.rect.centerx  # adjust small differences
            for block in blocks:
                block.rect.move_ip(0, 42)
                if block.rect.bottom == MAX_LINE * 42:
                    done = True
            balls.add(Ball(*chief_ball.rect.center))
            blocks.add(generate_blocks(.5, max(5, int(len(balls)*2))))
    
    DISPLAYSURF.fill(WHITE)
    pg.draw.circle(DISPLAYSURF, RED, pg.mouse.get_pos(), 10)
    arrow_image_rot = pg.transform.rotate(arrow_image, direction/np.pi*180)
    if phase == 0:
        DISPLAYSURF.blit(
            arrow_image_rot,
            arrow_image_rot.get_rect(center=chief_ball.rect.center))
    balls.draw(DISPLAYSURF)
    blocks.draw(DISPLAYSURF)
    info_text(DISPLAYSURF, f'Score: {score}', 16, bottomleft=(0, WINDOWHEIGHT))
    info_text(DISPLAYSURF, f'Balls: {len(balls)}', 16, bottomright=(WINDOWWIDTH, WINDOWHEIGHT))
    pg.display.flip()

info_text(DISPLAYSURF, 'GAME OVER!', 32, center=(WINDOWWIDTH//2, WINDOWHEIGHT//2))
pg.display.flip()

while True:
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()
