from pygame import init, SRCALPHA, Color, draw, font, Surface
from colors import *

init()

f_arial = font.Font('arial.ttf', 14)
#f_arial = font.Font('consola.ttf', 12)

def display_text(surf, text, x, y):

    max_w = 0
    for line in text:
        str_w = f_arial.render(line, False, WHITE).get_width()
        if str_w > max_w:
            max_w = str_w

    w = max_w - 1 + 10

    strings = len(text)
    h = strings * 20 - 4 + 20
    s = Surface((w, h), flags=SRCALPHA)
    s.fill(Color(0, 0, 0, 130))

    delay = 0
    for line in text:
        s.blit(f_arial.render(line, False, WHITE), (5, delay - 2 + 5))
        delay += 18

    draw.rect(s, GRAY_DARK, (0, 0, w, h), 1)

    surf.blit(s, (x, y))