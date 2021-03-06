# -*- coding: utf-8 -*-

#
# Signa marks description
#

# - MARK_MACHINE
# Метка с именем машины, текст метки должен соответствовать PrintingPress.name
# - MARK_OUTPUTTER
# Кто выводит формы, текст метки должен соответствовать Outputter.name
# - MARK_PAPER
# Размер бумаги (печатного листа)

# в 15-й Сигне - одна метка tes_Outputter
# 'Выведено: Vonoel     Speedmaster 900.0 x 640.0'
# в 16-й Сигне - одна метка tes_Outputter
# 'Выведено: Vonoel     tes / Speedmaster 900.0 x 640.0'
# в 16-й сигне с 04.07.2015 - метки поменял на три раздельные - Outputter, Machine, Paper
# [Outputter]         [Machine]             [Paper]
# Выведено: Vonoel    Машина: Speedmaster   Бумага: 900.0 x 640.0


# формат метки - ['имя как пишется в Сигне', 'regexp, который должен вернуть желаемое']
MARKS_MACHINE = (
    ['Machine', r':\s(\w+)'],
    ['tes_Outputter', r'(\w+)\s\d+[.,]?\d*\s*x\s*\d+[.,]?\d*']
)
MARKS_OUTPUTTER = (
    ['Outputter', r':\s(\w+)'],
    ['tes_Outputter', r':\s(\w+)']
)
MARKS_PAPER = (
    ['Paper', r'(\d+[.,]?\d*)\s*x\s*(\d+[.,]?\d*)'],
    ['tes_Outputter', r'(\d+[.,]?\d*)\s*x\s*(\d+[.,]?\d*)']
)  # demo https://regex101.com/r/zS4gB2/1 - возвращает две группы (ширина и высота), работает как с точкой, так и с запятой