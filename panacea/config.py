# coding: utf-8

u"""
Конфигурационный файл приложения.

Работа с параметрами должна осуществляться по средствами вызовов
функций config.get(var_name)

Метод get реализован таким образом, что имеет приоритет на значения
из settings.py, таким образом все переменные, описанные в понфиге
могут быть переопределены
"""

from panacea.tools import _get
get = lambda name, **kwargs: _get(globals(), name, **kwargs)

__all__ = ['get']

# глобальный рубильник
PCFG_ENABLED = False

# префикс ключей в redis
PCFG_KEY_PREFIX = 'panacea:'

# разделитель частей ключа
PCFG_PART_SEPARATOR = ';'

# разделитель значений внутри части ключа
PCFG_VALUES_SEPARATOR = '&'

# дефолтное время жизни ключа в секундах
PCFG_DEFAULT_TTL = 600

# имя логгера по умолчанию
# если значение на задать, будет использован
# дефолтный логгер root
PCFG_LOGGER_NAME = None

# допустимые коды ответов для кеширвоания
PCFG_ALLOWED_STATUS_CODES = (200,)

# будут кешироваться только ответы данного ct
PCFG_ALLOWED_CONTENT_TYPE = 'application/json'


# структура конфигурации кеширования
# должна быть полностью переопределена в приложении
PCFG_CACHING = {
    # учитваемые по дефолту значения при построении ключа
    'key_defaults': {
        # всегда включаем в состав ключа эти ...
        # -"- get-параметра
        'GET': [],
        # -"- заголовки
        'META': [],
        # -"- куки
        'COOKIES': []
    },
    # в каком порядке учитывать блоки значений
    # сначала в ключе пойду параметры query_string(сначала дефолтные
    # в указанном порядке), затем, если указаны, то конкретные для схемы, также
    # в указанном порядке
    # дале по аналогии с остальными блоками: headers, cookies
    'key_defaults_order': ['GET', 'META', 'COOKIES'],

    # схемы кеширования
    'schemes': {
        # каждый ключ - alias django urlconf
        'some_urlconf_alias': {
            # необязательный ключ активности данной схемы,
            # по дефолту = True
            "enabled": True,
            # кастомные ключи для частей
            # из которых происходит состалвение ключа
            # добавляются к дефолтным значениям key_defaults
            "GET": [],
            "META": [],
            "COOKIES": []
        }
    }
}
