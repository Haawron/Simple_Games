import pygame as pg
from pygame.locals import *
import sys


WINDOW_WIDTH = 560
WINDOW_HEIGHT = 700
FPS = 60
GAME_TITLE = 'For Experiment'

WHITE = (255, 255, 255)
BLACK = (0,   0,   0  )

COLOR_BG = WHITE


def draw_text(surface, text, coord=(0, 0)):

    font = pg.font.Font('/System/Library/Fonts/Menlo.ttc', 32)
    textSurface = font.render(text, True, BLACK, WHITE)
    textRect = textSurface.get_rect()  # 텍스트 크기 정보도 들어있어서 이렇게 해야 됨
    textRect.center = coord

    surface.blit(textSurface, textRect)


def main():

    ########################################################################
    global FPSCLOCK, DISPLAYSURF  # 그냥 전역 변수 선언
    pg.init()
    pg.font.init()
    FPSCLOCK = pg.time.Clock()
    DISPLAYSURF = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pg.display.set_caption(GAME_TITLE)
    DISPLAYSURF.fill(COLOR_BG)
    ########################################################################

    while True:

        DISPLAYSURF.fill(COLOR_BG)
        # draw_text(DISPLAYSURF, 'RIGHT', (280, 350))

        pressed = pg.key.get_pressed()
        if any(pressed):

            if pressed[K_RIGHT]:
                draw_text(DISPLAYSURF, 'RIGHT', (280, 350))
            if pressed[K_LEFT]:
                draw_text(DISPLAYSURF, 'LEFT', (280, 350))
            if pressed[K_UP]:
                draw_text(DISPLAYSURF, 'UP', (280, 350))
            if pressed[K_DOWN]:
                draw_text(DISPLAYSURF, 'DOWN', (280, 350))

        else:
            draw_text(DISPLAYSURF, 'HI', (280, 350))

        for event in pg.event.get():

            if event.type == QUIT or\
                    (event.type == KEYUP and event.key == K_ESCAPE):
                # QUIT은 그냥 안전을 위해 넣음
                pg.quit()  # 게임 종료
                sys.exit()  # 다음 게임 안 하고 그냥 프로세스 종료

        pg.display.update()
        FPSCLOCK.tick(FPS)


if __name__=='__main__':
    while True:  # 이거 여기서 돌리면 안 될 것 같은데
        main()
