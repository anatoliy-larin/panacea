# coding: utf-8
__author__ = 'klem4'

VERSION = (0, 0, 2)
__version__ = '.'.join(map(str, VERSION))

from django.conf import settings
if settings.DEBUG:
    print "DEBUG: panacea %s" % __version__