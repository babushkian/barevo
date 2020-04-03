from random import randint

# цвета
BLACK = [0, 0, 0]
GRAY_DARK = [20, 20, 20]
GRAY = [100, 100, 100]
WHITE = [255, 255, 255]

GREEN = [20, 100, 20]
RED = [100, 20, 20]
BLUE = [20, 20, 100]


def color_mutation(color, rate, bottom_limit=0, top_limit=255):
    new_color = []
    for c in color:
        new_c = c + randint(-rate, rate)
        if new_c > top_limit:
            new_c = top_limit
        if new_c < bottom_limit:
            new_c = bottom_limit
        new_color.append(new_c)
    return new_color


def int_color(color):
    new_color = []
    for i in range(3):
        new_color.append(int(color[i]))
    return new_color


def mixing(color_1, color_2, balance=0.5):
    new_color = []
    for i in range(3):
        new_color.append(int(color_1[i] * balance + color_2[i] * (1 - balance)))
    return new_color


def float_mixing(color_1, color_2, balance=0.5):
    new_color = []
    for i in range(3):
        new_color.append(color_1[i] * balance + color_2[i] * (1 - balance))
    return new_color



def mixing_2(colors):
    r = 0
    g = 0
    b = 0
    for col in colors:
        r += col[0]
        g += col[1]
        b += col[2]
    r /= len(colors)
    g /= len(colors)
    b /= len(colors)
    return r, g, b


def brightness(color, shift):
    new_color = []
    for c in color:
        c += shift
        if c < 0:
            c = 0
        if c > 255:
            c = 255
        new_color.append(c)
    return new_color


def normal_color(color):
    new_color = []
    for ch in color:
        if ch > 255:
            new_color.append(255)
        elif ch < 0:
            new_color.append(0)
        else:
            new_color.append(ch)
    return new_color


def random_color():
    return [randint(0, 255) for _ in range(3)]
