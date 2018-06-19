import pygame as pg
from pygame.locals import *
import random
import sys

FPS = 60  # frames per second, the general speed of the program
WINDOWWIDTH = 560  # size of window's width in pixels
WINDOWHEIGHT = 700  # size of windows' height in pixels
OBJSIZE = 30  # size of objects in pixels

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)


COLOR_BACKGROUND = WHITE
COLOR_POO = RED
COLOR_PLAYER = BLACK


class Const:
    G = 1512.6  # gravitational acc in pixels
    mu = .8  # sliding friction factor
    # mass = 10.  # effect on sliding friction
    acc = 2062.7  # player acc in pixels
    p = 1 / 15000  # initial poo generating prob
    p_update_rate = 1.35  # p will be updated every 10 seconds


class PhysicalEngine:

    def __init__(self):
        self.prev_vx = 0.
        self.prev_vy = 0.
        self.vx = 0.
        self.vy = 0.
        self.dt = 1 / FPS
        self.STOP_WHILE_MOVING = False
        self.acc = Const.acc - Const.mu * Const.G

    def acc_down(self, rect):
        self.__store()
        self.vy += Const.G * self.dt
        self.__move(rect)

    def acc_left(self, rect):
        self.__store()
        self.vx -= self.acc * self.dt
        self.__move(rect)

    def acc_right(self, rect):
        self.__store()
        self.vx += self.acc * self.dt
        self.__move(rect)

    def stay(self, rect):
        self.__store()
        if self.vx != 0:
            self.vx -= self.prev_vx / abs(self.prev_vx) * Const.mu * Const.G * self.dt
        # friction cannot change the direction of the object
        if self.prev_vx * self.vx < 0:
            self.vx = 0.
            self.STOP_WHILE_MOVING = True
        self.__move(rect)

    def __store(self):
        self.STOP_WHILE_MOVING = False
        self.prev_vx = self.vx
        self.prev_vy = self.vy

    def __move(self, rect):
        if not self.STOP_WHILE_MOVING:
            ds_x = .5 * self.dt * (self.prev_vx + self.vx)
            ds_y = .5 * self.dt * (self.prev_vy + self.vy)

        else:
            ds_x = -.5 * (self.prev_vx ** 2) / self.acc
            ds_y = -.5 * (self.prev_vy ** 2) / self.acc

        rect.x += round(ds_x)
        rect.y += round(ds_y)

        if rect.center[0] < 0:
            rect.x = - (rect.size[0] // 2)
            self.vx = 0.

        if rect.center[0] >= WINDOWWIDTH:
            rect.x = WINDOWWIDTH - 1 - rect.size[0] // 2
            self.vx = 0.

        if rect.center[1] >= WINDOWHEIGHT:
            rect.y = WINDOWHEIGHT - rect.size[1] // 2
            self.vy = 0.


class Block(pg.sprite.Sprite):


    def __init__(self, color, coord=(0, 0)):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((OBJSIZE, OBJSIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = coord
        self.engine = PhysicalEngine()

    def move_down(self):
        self.engine.acc_down(self.rect)  # rect is modified

    def move_left(self):
        self.engine.acc_left(self.rect)

    def move_right(self):
        self.engine.acc_right(self.rect)

    def stay(self):
        self.engine.stay(self.rect)


def draw_text(surface, text, coord=(0, 0)):
    font = pg.font.Font(r'Menlo-Regular.ttf', 32)
    textSurface = font.render(text, True, BLACK, WHITE)
    textRect = textSurface.get_rect()
    textRect.center = coord

    surface.blit(textSurface, textRect)
    # pg.display.update()


def main():

    global FPSCLOCK, DISPLAYSURF
    pg.init()
    FPSCLOCK = pg.time.Clock()
    DISPLAYSURF = pg.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pg.display.set_caption('Dodge Poo! By Haawron')

    DISPLAYSURF.fill(WHITE)

    player = Block(RED, ((WINDOWWIDTH - OBJSIZE) // 2,
                         WINDOWHEIGHT - OBJSIZE))
    poo_list = pg.sprite.RenderPlain()
    all_sprites_list = pg.sprite.RenderPlain()
    all_sprites_list.add(player)

    score = 0
    frame_count = 0
    p = Const.p  # initial p
    while True:

        frame_count += 1

        DISPLAYSURF.fill(WHITE)

        # check the collision
        if pg.sprite.spritecollide(player, poo_list, True):
            draw_text(DISPLAYSURF, 'Game Over!', (WINDOWWIDTH // 2, 150))
            draw_text(DISPLAYSURF, 'Score : {}'.format(score), (WINDOWWIDTH // 2, 350))
            draw_text(DISPLAYSURF, 'Press [Enter] to Restart', (WINDOWWIDTH // 2, 550))
            pg.display.update()

            while True:
                pressed = pg.key.get_pressed()
                if not all(a == 0 for a in pressed):

                    if pressed[K_RETURN]:
                        return

                for event in pg.event.get():
                    if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                        pg.quit()
                        sys.exit()

        draw_text(DISPLAYSURF, 'Score : {}'.format(score), (100, 30))

        # new poo on every top pixel
        for x in range(WINDOWWIDTH):
            if random.random() < p:
                poo = Block(BLACK, (x, 0))
                poo_list.add(poo)
                all_sprites_list.add(poo)

        all_sprites_list.draw(DISPLAYSURF)

        # update p at every 10 seconds
        if frame_count % (FPS * 10) == 0:
            p *= Const.p_update_rate

        # poos are falling
        for poo in poo_list:
            poo.move_down()
            if poo.rect.y == WINDOWHEIGHT - OBJSIZE // 2:
                poo.kill()
                score += 1

        # key down event handling
        pressed = pg.key.get_pressed()
        # if not all(a == 0 for a in pressed):
        if any(pressed):

            if pressed[K_RIGHT]:
                # "accelerate" to right
                player.move_right()

            elif pressed[K_LEFT]:
                # "accelerate" to left
                player.move_left()

            elif pressed[K_NUMLOCK]:
                player.stay()

        else:
            # "decelerate"
            player.stay()

        # event handling
        for event in pg.event.get():

            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pg.quit()
                sys.exit()

        pg.display.update()
        FPSCLOCK.tick(FPS)

if __name__ == '__main__':
    while True:
        main()
