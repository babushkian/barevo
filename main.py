import random

import pygame as pg

import pg_events as pg_e
import pg_textblocks
import grid_tools as gt
from colors import *


RES = 100 # разрешение игрового поля
C_SIZE = 5 # линейный размер клетки впикселях
G_SIZE = 8 ** 2 # размер генома
MULT_PROTEIN = 4
END_CYCLE = 8001 # симуляция заканчивается на этом цикле


#SEED = 669 # сид рандома для повторения результата
#random.seed(SEED)


class Object:

    """
    Любой объект (организм, либо что-то еще, например различные препятствия) имеет следующие параметры:
    координаты X Y и цвет, а так же занимает не более одной клетки (единицы пространства) виртуального мира.
    В одной клетке может содержаться не более одного объекта.
    """

    def __init__(self, x, y, color):

        # При инициализации объект сразу же помещается в клетку виртуального мира. См. модуль grid_tools
        self.cell = grid.cell(x, y)
        self.cell.cont = self

        self.x = x
        self.y = y
        self.rect = pg.Rect(self.x * C_SIZE, self.y * C_SIZE, C_SIZE, C_SIZE)
        self.color = color

    def draw(self, surf):

        surf.fill(self.color, self.rect)


class Bot(Object):

    """
    Любой бот может быть живым или умершим. Единственный общий атрибут -- количество белка внутри организма.
    """

    def __init__(self, x, y, color):

        super().__init__(x, y, color)
        self.protein = 0


class DeadBot(Bot):

    """
    Для начала рекомендуется ознакомиться с классом AliveBot.
    После смерти живого бота, на его месте появляется мертвый бот, имеющий в себе количество белка, равное количеству
    белка внутри живого бота на момент смерти. При смерти бот становится в два раза темнее. Мертвый бот имеет свой
    таймер существования, по истечению которого полностью исчезает.
    """

    def __init__(self, x, y, color):

        # Функция, смешивающая два цвета, см. модуль colors
        color = float_mixing(color, BLACK, 0.5)
        super().__init__(x, y, color)
        self.timer = 160 * 2

    def decay(self):

        global free_protein

        self.timer -= 1
        # со временем мертвец постепенно темнеет
        self.color = float_mixing(self.color, BLACK, 0.995)

        X = 1
        if self.protein >= X:
            self.protein -= X
            free_protein += X

        if self.timer <= 0:
            dead_bots.remove(self)

            # при удалении мертвеца не забываем сделать клетку, в которой он находился, пустой
            self.cell.cont = None
            free_protein += self.protein

import genome as gm

class AliveBot(Bot):

    """
    Продолжительность жизни бота ограничена, по истечению таймера он погибает. На каждом цикле отнимается
    единица таймера. Некоторые команды (действия бота) могут дополнительно отнимать единицы таймера или же прибавлять.
    Я называю это системой штрафов и она создана для соблюдения баланса в мире.
    """

    def __init__(self, x, y, color, gc, stat):
        global bot_last_number
        bot_last_number += 1
        global bots_counter
        bots_counter += 1
        super().__init__(x, y, color)
        self.stat = stat
        self.genome = gm.Genome(gc)
        self.timer = 160

        self.id = bot_last_number
        self.all_consumed_protein = 0 # протеин, потребленный за всю жизнь
        self.protein_plant = 0
        self.protein_predator = 0
        self.protein_mushroom = 0
        self.moves = 0 # склько перемещений сделал бот
        self.children = 0 # сколько раз бот делился
        self.death_cycle = None


    def get_around(self):
        # См. модуль grid_tools
        around = self.cell.moore_neighborhood
        self.available_cells = around[:4]

        # Прикольная штука. Если, например, и верхняя и правая клетки чем-то заняты, то и клетка сверху-справа
        # не будет доступна боту.
        if around[0].cont is None or around[1].cont is None: self.available_cells.append(around[4])
        if around[1].cont is None or around[2].cont is None: self.available_cells.append(around[5])
        if around[2].cont is None or around[3].cont is None: self.available_cells.append(around[6])
        if around[3].cont is None or around[0].cont is None: self.available_cells.append(around[7])

        # Тут мы получаем два списка: список пустых клеток вокруг и список объектов вокруг
        self.void_around = []
        self.objects_around = []
        for c in self.available_cells:
            if c.cont is None: self.void_around.append(c)
            else: self.objects_around.append(c.cont)


    def mult(self):
        # размножение
        cell = random.choice(self.void_around)
        x, y = cell.x, cell.y
        color = color_mutation(self.color, 5)
        self.children += 1

        # Случайная цифра в геноме меняется
        new_bot = AliveBot(x, y, color, self.genome.gcode, self.stat)

        # это нужно чтобы проклятые числа с плавающей точкой не округлялись и общее количество белка в мире не менялось
        p = int(self.protein / 2)
        new_bot.protein = p
        self.protein -= p

        new_gen.append(new_bot)

    def die(self):

        # Смерть. Тут удаляется бот и появляется мертвый бот
        global bots_counter
        bots_counter -= 1
        self.death_cycle = cycle
        self.stat.add_to_measure_pool(self)
        bots.remove(self)
        dead_bot = DeadBot(self.x, self.y, self.color)
        dead_bot.protein = self.protein
        dead_bots.append(dead_bot)


    def live(self):

        global free_protein
        global oxygen
        global carbon

        # чтение генома и выполнение команд тут! И вообще вся его жизнь
        self.timer -= 1
        count = 0
        run = True
        '''
        if self.id < 0:
            print('Бот %5d указатель: %3d значенте: %3d'% (self.id, self.genome._counter, self.genome.command()))
            
        '''
        while run:

            # если таймер бота кончился, он умирает
            if self.timer <= 0:
                self.die()
                run = False

            # если внутри бота накопилось уж очень много белка, а в геноме так и не попалась команда размножения,
            # бот постарается размножиться. Если у него не получится (вокруг тупо нет свободного места),
            # то ничего страшного
            elif self.protein >= MULT_PROTEIN * 10:
                self.get_around()
                if len(self.void_around) >= 1:
                    self.mult()
                    run = False

            # возврат в начало кода
            elif self.genome.command() == 0:
                self.genome.counter_reset()

            # размножение
            elif self.genome.command() == 1:
                self.get_around()
                # Размножаться можно только если вокруг есть хотя бы одна свободная клетка и накоплено достаточно белка
                if len(self.void_around) >= 1 and self.protein >= MULT_PROTEIN:
                    self.mult()
                    self.genome.counter_condit_move(1) # условные переходы надо делать прямо в геноме
                    run = False
                # если не получилось выполнить команду деления, то выполнится какая-то другая команда
                else:
                    self.genome.counter_condit_move(2)

            # фотосинтез. Высасываем белок из мира путем превращения угл. газа в кислород
            elif self.genome.command() == 2:
                # Почувствовать себя растением можно только если в мире есть хотя бы одна единица углекислого газа
                # и одна единица белка
                if free_protein >= 1 and carbon >= 1:
                    free_protein -= 1
                    self.protein += 1
                    self.all_consumed_protein += 1
                    self.protein_plant += 1
                    carbon -= 1
                    oxygen += 1
                    # чуть-чуть зеленеем
                    self.color = float_mixing(self.color, (50, 200, 50), 0.97)
                    self.genome.counter_condit_move(1)
                    run = False
                else:
                    self.genome.counter_condit_move(2)

            # атака. Вообще, правильнее назвать это "воровством белка" т.к. не наносит урон
            elif self.genome.command() == 3:
                self.get_around()
                bots_around = []
                # целью может быть только живой бот
                for o in self.objects_around:
                    if isinstance(o, AliveBot):
                        if o.protein >= 1:
                            bots_around.append(o)
                # атаковать можно только если вокруг есть хотя бы один бот, а в мире присутствует кислород
                # превращает кислород в угл. газ. Типа дыхание
                if len(bots_around) > 0 and oxygen >= 1:
                    target = random.choice(bots_around)
                    self.protein += 1
                    self.all_consumed_protein += 1
                    self.protein_predator += 1
                    target.protein -= 1
                    oxygen -= 1
                    carbon += 1
                    self.color = float_mixing(self.color, (200, 50, 50), 0.97)
                    self.genome.counter_condit_move(1)
                    run = False
                else:
                    self.genome.counter_condit_move(2)

            # тупо питание. Высасывает белок из мира, и для этого не нужны никакие кислороды и углекислые газы.
            # При том сильно бъет по здоровью -- отнимает таймер. Таким образом, боты, получающие белок данным способом
            # не зависят от других веществ, но не смогут выдержать конкуренции
            # с более специализированными способами питания
            elif self.genome.command() == 4:
                if free_protein >= 1:
                    free_protein -= 1
                    self.protein += 1
                    self.all_consumed_protein += 1
                    self.protein_mushroom +=1
                    self.color = float_mixing(self.color, (100, 100, 100), 0.97)
                    self.timer -= 10
                    self.genome.counter_condit_move(1)
                    run = False
                else:
                    self.genome.counter_condit_move(2)

            # тупо перемещение в случайную свободную клетку по соседству
            elif self.genome.command() == 5: # команды надо делать прямо в геноме и без elif словарем {код команды: функция}
                self.get_around()
                if len(self.void_around):
                    cell = random.choice(self.void_around)
                    self.moves += 1
                    self.cell.cont = None
                    self.cell = cell
                    self.cell.cont = self
                    self.x, self.y = cell.x, cell.y
                    self.rect = pg.Rect(self.x * C_SIZE, self.y * C_SIZE, C_SIZE, C_SIZE)
                    self.color = float_mixing(self.color, (255, 255, 255), 0.999)
                    self.genome.counter_condit_move(1)
                    run = False
                else:
                    self.genome.counter_condit_move(2)

            # безусловный переход
            else:
                self.genome.counter_move() # не сдвигает указатель, а прыгает в новую ячейку


            # если бот выполнит две бесполезные команды (такие как безусловный переход) два раза, то он идет найух
            # и управление передается следующему боту
            count += 1
            if count >= 2:
                # self.die()
                run = False



    def bot_info(self):
        print('------------------------------')
        print('Номер бота: %d' % self.id)
        print('Сделано шагов: %d' % self.moves)
        print('Порождено потомков: %d' % self.children)
        print('Поглощено протеина: %d' % self.all_consumed_protein)
        print('Из фотосинтеза: %d' % self.protein_plant)
        print('Из хищничества: %d' % self.protein_predator)
        print('добыто естественно: %d' % self.protein_mushroom)

    def bot_info_string(self):
        s = '%d\t' % self.id
        s += '%d\t' % self.moves
        s += '%d\t' % self.children
        s += '%d\t' % self.all_consumed_protein
        s += '%d\t' % self.protein_plant
        s += '%d\t' % self.protein_predator
        s += '%d\t'  % self.protein_mushroom
        #s += '%s' % self.genome.gcode вывод всего генома пока не нужен
        return s





# тут генерируется стартовая популяция ботов (n особей) со случайным геномом
def bots_gen(n):
    global void_cells
    bots = []
    for i in range(n):
        pos = random.choice(void_cells)
        void_cells.remove(pos)
        x, y = grid.pos2xy(pos)
        color = [random.randint(0, 255) for _ in range(3)]
        genome = [random.randint(0, G_SIZE - 1) for _ in range(G_SIZE)]
        bots.append(AliveBot(x, y, color, genome, stat))
    return bots




free_protein = 3000
oxygen = 1000
carbon = 1000
bot_last_number = 0


import statistics
stat = statistics.Statistics()

# создаем квадратную сетку мира RES x RES клеток
grid = gt.Grid(RES)

# это всякие пайгеймовские штучки, инициализация, создание окна
pg.init()
DISP_RES = (RES * C_SIZE, RES * C_SIZE)
screen = pg.display.set_mode(DISP_RES)
clock = pg.time.Clock()

void_cells = [pos for pos in range(RES * RES)] # итзнасально все клетки экапна пустые
bots_counter = 0
bots = bots_gen(300)
dead_bots = []


surf_bots = pg.Surface((RES * C_SIZE, RES * C_SIZE), flags=pg.SRCALPHA)

cycle = 0
running = True



while running:

    mouse = pg.mouse.get_pos()
    pg_e.check_events()
    if pg_e.window_exit:
        running = False

    for d in dead_bots:
        d.decay()

    # перемешиваем список ботов, чтобы они обрабатывались в случайном порядке. Так будет честно!
    random.shuffle(bots)
    new_gen = []
    for b in bots:
        b.live()
    bots += new_gen

    # ========== ОТРИСОВКА ==========

    screen.fill(BLACK)
    surf_bots.fill(BLACK)
    for b in bots:
        b.draw(surf_bots)
    for d in dead_bots:
        d.draw(surf_bots)
    screen.blit(surf_bots, (0, 0))

    # шняга текст на экран выводит
    text_1 = ['time: {}'.format(cycle),
              'last bot: {}'.format(bot_last_number),
              'fps: {}'.format(round(clock.get_fps(), 1)),
              'bots: {}'.format(bots_counter),
              'free protein: {}'.format(free_protein),
              'carbon: {}'.format(carbon),
              'oxygen: {}'.format(oxygen)]
    pg_textblocks.display_text(screen, text_1, 5, 5)

    pg.display.flip()
    clock.tick(60)
    cycle += 1

    if cycle % stat.MEASURE_PERIOD ==0:
        stat.count(cycle)

    if cycle > END_CYCLE:
        running = False


stat.align_bots()
stat.write_all_bot_statistics(cycle)

print('Циклов симуляции: %d' % cycle)
print('Живые боты: %d' % len(bots))
print('Отживщие боты: %d' % stat.sample_size())
speed = sorted(stat.all_bots, key=lambda x: x.moves)
speed_champion = speed.pop()
print('Максимальный пробег: %d   |Бот: %06d' % (speed_champion.moves, speed_champion.id))
breed = sorted(stat.all_bots, key=lambda x: x.children)
breed_champion = breed.pop()
print('Макс. кол-во делений: %d  |Бот: %06d' % (breed_champion.children, breed_champion.id))

print('Топ ботов по передвижению:')
stat.bot_stat(speed, 3)
print('Топ ботов по размножению:')
stat.bot_stat(breed, 3)
