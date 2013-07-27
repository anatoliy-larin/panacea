# coding: utf-8

u"""
Конфигурационный файл приложения.

Типы ключей:
 - PCFG_* - параметры приложения, не имеющие отношения к
    схемам кеширования

 - PSHM_* - параметры, непосредственно относящиеся
    к схемам кеширования

Работа с параметрами должна осуществляться по средствами вызовов
функций config.get(var_name)

Метод get реализован таким образом, что имеет приоритет на значения
из settings.py, таким образом все переменные, описанные в понфиге
могут быть переопределены
"""

from panacea.tools import _get
get = lambda name: _get(globals(), name)

__all__ = ['get']


##########################
# секция паарметров PCFG #
##########################

# префикс ключей в redis
PCFG_KEY_PREFIX = 'panacea.'

# имя логгера по умолчанию
# если значение на задать, логирование будет игнорироваться
PCFG_LOGGER_NAME = None


##########################
# секция паарметров PSHM #
##########################
