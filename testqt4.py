# Copyright (c) 2015-2016 Maciej Dems <maciej.dems@p.lodz.pl>
# See LICENSE file for copyright information.

import sys
from pysparkle import PySparkle

try:
    from PySide import QtGui
except ImportError:
    from PyQt4 import QtGui



app = QtGui.QApplication(sys.argv)
sparkle = PySparkle('http://sparkle-project.org/files/sparkletestcast.xml', 'Sparkle Test App', '1.0', show_notes=False)
# sparkle = PySparkle('https://raw.githubusercontent.com/yahoo/Sparkle/master/Sample%20Appcast.xml',
# 'Sparkle Test App', '1.5')

