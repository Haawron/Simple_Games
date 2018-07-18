import pygame as pg
from pygame.locals import *
import sys
import queue
import numpy as np


FPS = 30  # frames per second, the general speed of the program
WINDOWWIDTH = 149  # size of window's width in pixels
WINDOWHEIGHT = 149  # size of windows' height in pixels

BLOCKSIZE = 5
GAP = 2

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
APPLE = (180, 180, 255)

COLOR_BACKGROUND = BLACK
COLOR_WORM = RED


def get_coord(box_number):
    return GAP + (BLOCKSIZE + GAP) * box_number[0], GAP + (BLOCKSIZE + GAP) * box_number[1]


class Block(pg.sprite.Sprite):

    def __init__(self, color, box_number=(0, 0)):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((BLOCKSIZE, BLOCKSIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(get_coord(box_number))
        self.box_number = list(box_number)

    def move(self, pressed_keys):
        unit = BLOCKSIZE + GAP
        get_cross = False
        if pressed_keys == K_UP:
            if self.box_number[1] == 0:
                self.box_number[1] = 20
                get_cross = True
            else:
                self.rect.move_ip(0, -unit)
                self.box_number[1] -= 1
        if pressed_keys == K_DOWN:
            if self.box_number[1] == 20:
                self.box_number[1] = 0
                get_cross = True
            else:
                self.rect.move_ip(0, unit)
                self.box_number[1] += 1
        if pressed_keys == K_LEFT:
            if self.box_number[0] == 0:
                self.box_number[0] = 20
                get_cross = True
            else:
                self.rect.move_ip(-unit, 0)
                self.box_number[0] -= 1
        if pressed_keys == K_RIGHT:
            if self.box_number[0] == 20:
                self.box_number[0] = 0
                get_cross = True
            else:
                self.rect.move_ip(unit, 0)
                self.box_number[0] += 1
        if get_cross:
            self.rect.x, self.rect.y = get_coord(self.box_number)


class Worm():

    def __init__(self):
        self.head = Block(RED, (10, 10))
        self.head1 = pg.sprite.Group()
        self.body = pg.sprite.Group()
        self.worm = pg.sprite.Group()
        self.worm.add(self.head)
        self.head1.add(self.head)

        self.body_q = queue.Queue(500)
        self.order_q = queue.Queue(500)

        self.just_added = False

    def move(self, pressed_keys):
        self.head.move(pressed_keys)
        self.order_q.put(pressed_keys)

        if not self.just_added:
            for part, order in zip(self.body_q.queue, self.order_q.queue):
                part.move(order)
            self.order_q.get(False)
        self.just_added = False

    def add(self):
        new_body = Block(GREEN, self.head.box_number)
        self.body.add(new_body)
        self.worm.add(new_body)
        self.body_q.put(new_body)
        self.just_added = True

    def display(self, surface):
        self.body.draw(surface)
        self.head1.draw(surface)


def set_apple(group, player):
    random_matrix = np.random.random([21, 21])
    p = 1 / (21 * 21 * FPS * 5)
    apples = []
    for box_number in zip(*np.where(random_matrix < p)):
        apple = Block(WHITE, box_number)
        # x, y = box_number
        # apple2 = pg.Rect((get_coord((x+1, y)), (BLOCKSIZE, BLOCKSIZE)))
        # apple3 = pg.Rect((get_coord((x, y+1)), (BLOCKSIZE, BLOCKSIZE)))
        # apple4 = pg.Rect((get_coord((x+1, y)), (BLOCKSIZE, BLOCKSIZE)))
        # apple.rect.union_ip(apple2)
        # apple.rect.union_ip(apple3)
        # apple.rect.union_ip(apple4)
        if not pg.sprite.spritecollide(apple, player.worm, False):
            group.add(apple)
            apples.append(box_number)
        else:
            apple.kill()
    return apples


def keydown_event_handler(prev_key, player):
    key = prev_key

    pressed = pg.key.get_pressed()
    if any(pressed):
        if pressed[K_RIGHT]:
            key = K_RIGHT
        elif pressed[K_LEFT]:
            key = K_LEFT
        elif pressed[K_DOWN]:
            key = K_DOWN
        elif pressed[K_UP]:
            key = K_UP

    if key:
        player.move(key)

    return key


def event_handler():
    for event in pg.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pg.quit()
            sys.exit()


def draw_text(surface, text, coord=(0, 0)):
    font = pg.font.Font('Menlo-Regular.ttf', 32)
    textSurface = font.render(text, True, BLACK, WHITE)
    textRect = textSurface.get_rect()
    textRect.center = coord

    surface.blit(textSurface, textRect)


def is_there_apple(apples):
    return len(apples.sprites()) != 0


def main():
    pg.init()
    FPSCLOCK = pg.time.Clock()
    DISPLAYSURF = pg.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pg.display.set_caption('SWEEP_WORM! By Haawron')

    DISPLAYSURF.fill(COLOR_BACKGROUND)

    player = Worm()
    apples = pg.sprite.Group()
    key = 0
    apple_on_field_count = 0

    while True:

        DISPLAYSURF.fill(COLOR_BACKGROUND)

        # =========================================================
        if pg.sprite.spritecollide(player.head, apples, True):
            player.add()
        set_apple(apples, player)
        apples.draw(DISPLAYSURF)
        if is_there_apple(apples):
            apple_on_field_count += 1
        else:
            apple_on_field_count = 0

        if apple_on_field_count == FPS * 8:
            draw_text(DISPLAYSURF, 'Game Over!', (WINDOWWIDTH // 2, 75))
            pg.display.update()

            while True:
                pressed = pg.key.get_pressed()
                if any(pressed):

                    if pressed[K_RETURN]:
                        return

                event_handler()
        # =========================================================


        player.display(DISPLAYSURF)
        key = keydown_event_handler(key, player)
        event_handler()
        pg.display.update()
        FPSCLOCK.tick(FPS)


if __name__=='__main__':
    while True:
        main()
