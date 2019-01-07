import numpy as np
import pygame as pg
from pygame.locals import *
from pygame import gfxdraw


up    = 0
down  = 1
left  = 2
right = 3

FPS             = 60
WINDOW_WIDTH    = 560  # 4의 배수
WINDOW_HEIGHT   = 700
PLAIN_MARGIN    = 60  # 좌/우/하단 마진, 4의 배수
NUMBLOCK_MARGIN = 10

PLAIN_WIDTH  = PLAIN_HEIGHT = WINDOW_WIDTH - 2 * PLAIN_MARGIN
OBJSIZE      = PLAIN_WIDTH // 4 - 2 * NUMBLOCK_MARGIN  # size of number boxes in pixels
UPPER_MARGIN = WINDOW_HEIGHT - PLAIN_HEIGHT - PLAIN_MARGIN

WHITE = (0, 0, 0)


############################################################################
############################### Rounded Rect ###############################
############################################################################
# https://github.com/Mekire/rounded-rects-pygame/blob/master/roundrects/roundrects.py

def aa_round_rect(surface, rect, color, rad=20, border=0, inside=(0,0,0)):
    """
    Draw an antialiased rounded rect on the target surface.  Alpha is not
    supported in this implementation but other than that usage is identical to
    round_rect.
    """
    rect = pg.Rect(rect)
    _aa_render_region(surface, rect, color, rad)
    if border:
        rect.inflate_ip(-2*border, -2*border)
        _aa_render_region(surface, rect, inside, rad)


def _aa_render_region(image, rect, color, rad):
    """Helper function for aa_round_rect."""
    corners = rect.inflate(-2*rad-1, -2*rad-1)
    for attribute in ("topleft", "topright", "bottomleft", "bottomright"):
        x, y = getattr(corners, attribute)
        gfxdraw.aacircle(image, x, y, rad, color)
        gfxdraw.filled_circle(image, x, y, rad, color)
    image.fill(color, rect.inflate(-2*rad,0))
    image.fill(color, rect.inflate(0,-2*rad))

############################################################################
############################################################################
############################################################################


class Animator:

    def __init__(self):
        self.path = []

    def move(self, rect, direction=up):
        # 진짜 움직이기만 해줌
        pass

    def calc(self, current, target, time, function='linear'):
        '''
        current에서 target까지 time만에 갈 수 있도록 계산
        time을 FPS에 맞춰 frame으로 변환 후 function에 따라
        각 frame에서의 위치를 list로 반환

        구간은 0~1로 변환 후 계산 뒤 다시 scaling

        Args:
            current:
            target:
            time: animate 하는 데에 걸리는 시간
            function: 'linear', ...
            :return:
        '''
        # https://gist.github.com/gre/1650294
        easing_functions = {
            'linear':         lambda x: x,
            'easeInQuad':     lambda x: x**2,
            'easeOutQuad':    lambda x: x*(2-x),
            'easeInOutQuad':  lambda x: np.where(x<.5, 2*x**2, -1+(4-2*x)*x),
            'easeInCubic':    lambda x: x**3,
            'easeOutCubic':   lambda x: (x-1)**3+1,
            'easeInOutCubic': lambda x: np.where(x<.5, 4*x**3, (x-1)*(2*x-2)**2+1),
            'easeInQuart':    lambda x: x**4,
            'easeOutQuart':   lambda x: 1-(x-1)**4,
            'easeInOutQuart': lambda x: np.where(x<.5, 8*x**4, 1-8*(x-1)**4),
            'easeInQuint':    lambda x: x**5,
            'easeOutQuint':   lambda x: 1+(x-1)**5,
            'easeInOutQuint': lambda x: np.where(x<.5, 16*x**5, 1+16*(x-1)**5)
        }

        d = target - current  # 음수여도 노상관
        frames = time * FPS
        x = np.linspace(0, 1, frames)
        y = easing_functions[function](x)
        y = d * y + current

        self.path = y


class NumBlock(pg.sprite.Sprite):

    colors = [
        (0, 0, 0), (1, 2, 3)
    ]

    def __init__(self, num=2, loc=(0, 0)):
        '''
        Args:
            num:
            loc: 생성되는 블럭의 위치, 칸 번호이고 왼쪽 위에서부터 오른쪽 밑으로 오름차순
        '''
        # 다이아몬드 상속시 맨 위 생성자 두 번 호출되는 걸 방지
        # 파이썬 3은 그냥 super()만 쓰세욤.
        super().__init__(self)
        self.image = pg.Surface((OBJSIZE, OBJSIZE))
        self.image.fill(self.colors[int(np.log2(num))])
        self.rect = self.image.get_rect()

        coordx = PLAIN_MARGIN + PLAIN_WIDTH // 4 * loc[0] + NUMBLOCK_MARGIN
        coordy = UPPER_MARGIN + PLAIN_HEIGHT // 4 * loc[1] + NUMBLOCK_MARGIN
        self.rect.x, self.rect.y = coordx, coordy
        self.animator = Animator()

        font = pg.font.Font('Menlo-Regular.ttf', 11).set_bold(True)
        textSurface = font.render(num, True, WHITE, None)
        textRect = textSurface.get_rect()
        textRect.center = self.rect.center

    def move(self, direction):
        self.animator.move(self.rect, direction)

    def draw(self):
        # Group.draw가 sprite.draw를 쓰는가?
        # 쓰는거면 걍 오버라이딩하면 댐
        pass