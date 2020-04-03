import random


class Genome:
    GENOME_SIZE = 64
    MUTATION_COEF = GENOME_SIZE / 10
    def __init__(self, gen = None):
        self.gcode = []
        self._counter = 0
        if gen:
            self.inherite_genome(gen)
        else:
            self.generate_genone()



    def inherite_genome(self, gen):
        '''
        наследуем геном от предка изменяем его в процессе мутации
        '''
        def get_mutant_amount():
            '''
            y = random.random() * 25 + 1
            y *= y
            x = self.MUTATION_COEF / y
            '''
            x = 1
            return x

        self.gcode = gen[:]
        # сколько генов мутируют
        mutant_genes_amount = get_mutant_amount()
        if mutant_genes_amount > 0:
            for i in range(mutant_genes_amount):
                self.gcode[random.randrange(self.GENOME_SIZE)] = random.randrange(self.GENOME_SIZE)

    def generate_genone(self):
        '''
        создаем геном дял первичных клеток в начале симуляции
        '''
        self.gcode = [random.randrange(self.GENOME_SIZE) for _ in range(self.GENOME_SIZE)]

    def counter_reset(self):
        self._counter = 0

    def counter_move(self, n=None):
        #переходит в ячейкув указанную ячейку
        # двигает указатель команды на n клеток вперед
        if n:
            self._counter = (self._counter + n) % self.GENOME_SIZE
        else:
            self._counter = (self._counter + self.command()) % self.GENOME_SIZE


    def command(self):
        return self.gcode[self._counter]

    def counter_condit_move(self, n):
        '''
        сдвигается на указанную ячейку и затем переходит на то число ячеек, которое уккзано в новой ячейке
        испошльзуется в условных переходах

        '''
        self.counter_move(n)

        self.counter_move(self.command())


    # тут два генома можно сравнить и узнать, сколько цифр в них отличается. Потом понадобится, например для команды атака
    def compare_genomes(self, other_genome):
        dif = 0
        for (g1, g2) in zip(self.gcode, other_genome.gcode):
            if g1 !=g2:
                dif += 1
        return dif
