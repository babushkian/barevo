"""
в объекте класса "Сетка" содержится список объектов класса "Ячейка" (клетка). В каждой ячейке что-то одно может лежать,
не более.
"""

class Grid:
    def __init__(self, res):
        self.res = res # размер квадратного цикличного поля

        self.cells = [] # все ячейки на поле
        for pos in range(res ** 2):
            x = pos % res
            y = pos // res
            self.cells.append(Cell(pos, x, y))

        for cell in self.cells:
            self.get_moore_neighborhood(cell)

    def cell(self, x, y):
        # возвращает обьект клетки по координатам
        return self.cells[y * self.res + x]

    def relative_position(self, x, y, dx, dy):
        # возвразает объект ячейки, смещенной относительно текущей координаты на циклическом поле
        x = (x + dx) % self.res
        y = (y + dy) % self.res
        return self.cell(x, y)

    def get_moore_neighborhood(self, cell):
        # возвращает объекты соседних клеток
        moves = ((-1, 0), (0, -1), (1, 0), (0, 1),
                 (-1, -1), (1, -1), (1, 1), (-1, 1))
        cell.moore_neighborhood = []
        for m in moves:
            cell.moore_neighborhood.append(self.relative_position(cell.x, cell.y, m[0], m[1]))

    def pos2xy(self, pos):
        x = pos % self.res
        y = pos // self.res
        return x, y


class Cell:
    def __init__(self, pos, x, y):
        self.pos = pos
        self.x = x
        self.y = y
        self.cont = None
        self.moore_neighborhood = []