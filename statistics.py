# здесь будет считаться и выводиться с татистика по миру
import csv

class Measured_value:
    '''
    Одна измеряемая величина - достается из атрибута бота. Какая именно, указана в строоке
    Несклдько таких величин содержатся в классе Specialization и обрабатываются однообразно
    '''
    def __init__(self, attribute, title):
        self.attribute = attribute
        self.title = title
        self.flush()

    def flush(self):
        '''
        основное здесь - это среднее значение, потому что счетчик особей и сумма величиныstati
        по всем особям - это технические, промежуточные числа. Счетчик особей можно востать
        из класса Specialization, вычислив длину списка особей. Так что возможно, что count
        даже лишний.
        Возможно здесь будут считаться не только среднее, но и медиана и дисперсия
        '''
        self.count = 0
        self.sum = 0
        self.avg = None

    def increment(self, bot):
        self.count += 1
        self.sum += getattr(bot, self.attribute)

    def average(self):
        if self.count > 0:
            self.avg =  self.sum / self.count
        else:
            self.avg = 0

    def display(self):
        return (self.title, self.avg)


class Specialization:
    '''
    Здесь содержаься все боты, которые удовлетворяют определенному условию.
    Функция-условие передается в качестве параметра
    '''
    MEASURE_VALUES = {'all_consumed_protein': 'протеин',  'children': 'дети', 'moves': 'ходы'}
    def __init__(self, name, compare_function, condition):
        self.is_condition = compare_function # функция, производящая отбор в страту
        self.condition = condition # условие по которому отбираются особи
        self.name = name
        self.measur_vals  = {}
        for measure in self.MEASURE_VALUES:
            self.measur_vals[measure] = Measured_value(measure, self.MEASURE_VALUES[measure])
        self.members = []

    def flush(self):
        for i in self.measur_vals.values():
            i.flush()
        self.members = []

    def check_profile(self, bot):
        return self.is_condition(bot, *self.condition)

    def check(self, bot):
        if self.check_profile(bot):
            for v in self.measur_vals.values():
                v.increment(bot)
            self.members.append(bot)

    def get_averages(self):
        for v in self.measur_vals.values():
            v.average()

    def count(self):
        return len(self.members)

    def return_measured_tuple(self, attribute):
        return self.measur_vals[attribute].display()


traits = {1:'protein_predator', 2:'protein_plant', 3:'protein_mushroom'}

def profile(bot, prime_feature, multiplier=1):
    prime = 0
    secondary = 0
    for feature in traits:
        if feature == prime_feature:
            prime += getattr(bot, traits[feature])
        else:
            secondary += getattr(bot, traits[feature])
    return prime > multiplier * secondary

def unexpressed(bot, a) :
    flag = True
    for main in traits:
        two_other  = 0
        for rest in traits:
            if rest != main:
                two_other += getattr(bot, traits[rest])
        one = getattr(bot, traits[main])
        if one > two_other:
            flag = False
            break
    return flag

def return_true(*a):
    return True


#species =['all', 'predator', 'plant', 'mushroom', 'unspecialized']
species =['все', 'хищники', 'растения', 'грибы', 'без специализации']

class Statistics:
    MEASURE_PERIOD = 200
    period_stat = open('bot_periodic_statistics.csv', 'w', encoding='UTF16')

    CONDITIONS = [[return_true, [None]],
                  [profile, [1, 1]],
                  [profile, [2, 1]],
                  [profile, [3, 1]],
                  [unexpressed, [None]]]

    def __init__(self):

        self.strates = []
        for i in range(len(Statistics.CONDITIONS)):
            self.strates.append(Specialization(species[i], *Statistics.CONDITIONS[i]))
        self.all_bots = []
        self.write_header()


    def add_to_measure_pool(self, bot):
        self.all_bots.append(bot)

    def flush_measure_pool(self):
        self.all_bots = []
        for strate in self.strates:
            strate.flush()

    def align_bots(self):
        self.all_bots = sorted(self.all_bots, key = lambda x: x.id)

    def sample_size(self):
        return len(self.all_bots)

    def bot_stat(self, some_bots_list, number=None):
        '''
        :param some_bots_list: отстртированный по какому-то критерию список ботов
        :param number: количество ботов, которых надо вывести (топ-n)
        :return: ничего, вызывает информацию о ботах в цикле
        '''
        if not number:
            number = len(some_bots_list)
        print('====================================')
        for i in range(-1, -1-number, -1): # с конца списка в обратном порядке
            some_bots_list[i].bot_info()

    def write_all_bot_statistics(self, cycle):

        header = "Номер бота\tСделано шагов\tПорождено потомков\tПоглощено протеина\tИз фотосинтеза\tИз хищничества\tдобыто естественно\n"
        file_name = './zoutput/bot_statistics_%s.csv' % cycle
        bot_record = open(file_name, 'w', encoding='UTF16')
        bot_record.write(header)
        for bot in self.all_bots:
            bot_record.write(bot.bot_info_string() + '\n')
        bot_record.close()


    def count(self, cycle):
        '''
        Основной метод для полсчета статистики
        '''
        for bot in self.all_bots:
            for strata in self.strates:
                strata.check(bot)
        for strata in self.strates:
            strata.get_averages()
        self.write_all_bot_statistics(cycle)
        self.write_strates(cycle)
        self.flush_measure_pool()


    def write_header(self):
        string = 'цикл'
        # записываем количество особей по стратам
        for strat in self.strates:
            string += '\t{}'.format(strat.name)
        # записываем средние значения измеряемых величин по стратам, поэтому нужны два цикла
        for v in Specialization.MEASURE_VALUES:
            for strat in self.strates:
                string += '\t{} {}'.format(strat.name, strat.return_measured_tuple(v)[0])
        string += '\n'
        self.period_stat.write(string)


    def write_strates(self, cycle):
        string = '%5d' % cycle
        # записываем количество особей по стратам
        for strat in self.strates:
            string += '\t{}'.format(strat.count())
        for v in Specialization.MEASURE_VALUES:
            for strat in self.strates:
                string += '\t{}'.format(strat.return_measured_tuple(v)[1])
        string +='\n'
        self.period_stat.write(string.replace('.', ','))
