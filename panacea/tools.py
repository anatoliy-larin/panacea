# coding: utf-8

from django.conf import settings
from django.core import urlresolvers

import logging

def resolve_path(request):
    try:
      return urlresolvers.resolve(request.path)
    except urlresolvers.Resolver404:
        pass
    except Exception as e:
        get_logger().error(e)


def _get(_globals, name, **kwargs):
    u"""
    метод для получения значения из конфига
    сначала ищем в settings, если параметра там нет
    то берем из вызываемого файла,
    если и так нет, то exception

    использование в модуле, на примере config.py:

    >>from panacea.tools import _get
    >>get = lambda name, **kwargs: _get(globals(), name, **kwargs)
    >>__all__ = ['get']

    далее после импорта config в любом месте:
    >>import config as conf
    >>conf.get('SOME_VARIABLE')
    >>conf.get('SOME_VARIABLE', default={})
    """

    try:
        return getattr(settings, name)
    except:
        try:
            return _globals[name]
        except KeyError:
            if 'default' in kwargs:
                return kwargs.get('default')


def get_logger():
    import panacea.config as conf
    return logging.getLogger(conf.get('PCFG_LOGGER_NAME'))
