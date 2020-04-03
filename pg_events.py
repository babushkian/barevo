import pygame as pg

window_exit = False
keydown_escape = False
lmb = False
mmb = False
rmb = False


def check_events():

    clear()

    global window_exit
    global keydown_escape
    global lmb
    global mmb
    global rmb

    for event in pg.event.get():

        if event.type == pg.QUIT:
            window_exit = True

        # нажатия клавиатуры
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                keydown_escape = True

        # нажатия мыши
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                lmb = True
            if event.button == 2:
                mmb = True
            if event.button == 3:
                rmb = True


def clear():

    global window_exit
    global keydown_escape
    global lmb
    global mmb
    global rmb

    window_exit = False
    keydown_escape = False
    lmb = False
    mmb = False
    rmb = False
