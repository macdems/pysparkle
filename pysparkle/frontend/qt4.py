# Copyright (c) 2015-2016 Maciej Dems <maciej.dems@p.lodz.pl>
# See LICENSE file for copyright information.

import sys
if 'PySide' in sys.modules:
    from PySide.QtCore import Qt
    from PySide import QtGui
elif 'PyQt4' in sys.modules:
    from PyQt4.QtCore import Qt
    from PyQt4 import QtGui
else:
    raise ImportError("cannot determine Qt bindings: import PySide or PyQt4 first")


def ask_for_autocheck(pysparkle):
    dialog = QtGui.QMessageBox()
    dialog.setIcon(QtGui.QMessageBox.Question)
    dialog.setWindowTitle(dialog.tr("Check for updates automatically?"))
    dialog.setText(dialog.tr("Should {} automatically check for updates?").format(pysparkle.appname))
    dialog.setInformativeText(dialog.tr("You can always check for updates manually from the menu."))
    dialog.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
    result = dialog.exec_()
    return result == QtGui.QMessageBox.Yes


def update_error(msg=None):
    dialog = QtGui.QMessageBox()
    dialog.setIcon(QtGui.QMessageBox.Critical)
    dialog.setWindowTitle(dialog.tr("Update Error!"))
    dialog.setText(dialog.tr("An error occurred in retrieving update information; "
                             "are you connected to the internet? Please try again later."))
    if msg is not None:
        dialog.setDetailedText(msg)
    dialog.setStandardButtons(QtGui.QMessageBox.Ok)
    dialog.exec_()


def no_info(pysparkle):
    dialog = QtGui.QMessageBox()
    dialog.setIcon(QtGui.QMessageBox.Warning)
    dialog.setWindowTitle(dialog.tr("No update information!"))
    dialog.setText(dialog.tr("There is no update information for {}.\n\n"
                             "Maybe the software is not supported for your operating system...")
                   .format(pysparkle.appname))
    dialog.setStandardButtons(QtGui.QMessageBox.Ok)
    dialog.exec_()


def no_update(pysparkle):
    dialog = QtGui.QMessageBox()
    dialog.setIcon(QtGui.QMessageBox.Information)
    dialog.setWindowTitle(dialog.tr("You're up to date!"))
    dialog.setText(dialog.tr("{} {} is currently the newest version available.")
                   .format(pysparkle.appname, pysparkle.appver))
    dialog.setStandardButtons(QtGui.QMessageBox.Ok)
    dialog.exec_()


def update_available(pysparkle, maxitem, items):
    dialog = QtGui.QMessageBox()
    dialog.setIcon(QtGui.QMessageBox.Information)
    dialog.setWindowTitle(dialog.tr("A new version of {} is available!").format(pysparkle.appname))
    dialog.setText(dialog.tr("{} {} is now available (you have {}).\n\nWould you like to download it now?")
                   .format(pysparkle.appname, maxitem['version'], pysparkle.appver))
    if any(item['notes'] for item in items):
        grid = dialog.layout()
        label = QtGui.QLabel(dialog.tr("Release notes:"))
        grid.addWidget(label, grid.rowCount(), 0, 1, grid.columnCount())
        notes = QtGui.QTextEdit()
        notes.setText("<br/>\n".join("<h3>{title}</h3>\n{notes}\n".format(**item) for item in items))
        notes.setFixedHeight(200)
        notes.setReadOnly(True)
        grid.addWidget(notes, grid.rowCount(), 0, 1, grid.columnCount())
        dialog.updateGeometry()
    get_button = dialog.addButton(dialog.tr("Get update"), QtGui.QMessageBox.YesRole)
    skip_button = dialog.addButton(dialog.tr("Skip this version"), QtGui.QMessageBox.NoRole)
    later_button = dialog.addButton(dialog.tr("Remind me later"), QtGui.QMessageBox.RejectRole)
    dialog.exec_()
    result = dialog.clickedButton()
    if result in (get_button, skip_button):
        return result == get_button
