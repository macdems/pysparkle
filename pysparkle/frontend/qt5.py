# Copyright (c) 2015-2016 Maciej Dems <maciej.dems@p.lodz.pl>
# See LICENSE file for copyright information.

import sys
from PyQt5 import QtWidgets


def ask_for_autocheck(pysparkle):
    dialog = QtWidgets.QMessageBox()
    dialog.setIcon(QtWidgets.QMessageBox.Question)
    dialog.setWindowTitle(dialog.tr("Check for updates automatically?"))
    dialog.setText(dialog.tr("Should {} automatically check for updates?").format(pysparkle.appname))
    dialog.setInformativeText(dialog.tr("You can always check for updates manually from the menu."))
    dialog.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    result = dialog.exec_()
    return result == QtWidgets.QMessageBox.Yes


def update_error(msg=None):
    dialog = QtWidgets.QMessageBox()
    dialog.setIcon(QtWidgets.QMessageBox.Critical)
    dialog.setWindowTitle(dialog.tr("Update Error!"))
    dialog.setText(dialog.tr("An error occurred in retrieving update information; "
                             "are you connected to the internet? Please try again later."))
    if msg is not None:
        dialog.setDetailedText(msg)
    dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
    dialog.exec_()


def no_info(pysparkle):
    dialog = QtWidgets.QMessageBox()
    dialog.setIcon(QtWidgets.QMessageBox.Warning)
    dialog.setWindowTitle(dialog.tr("No update information!"))
    dialog.setText(dialog.tr("There is no update information for {}.\n\n"
                             "Maybe the software is not supported for your operating system...")
                   .format(pysparkle.appname))
    dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
    dialog.exec_()


def no_update(pysparkle):
    dialog = QtWidgets.QMessageBox()
    dialog.setIcon(QtWidgets.QMessageBox.Information)
    dialog.setWindowTitle(dialog.tr("You're up to date!"))
    dialog.setText(dialog.tr("{} {} is currently the newest version available.")
                   .format(pysparkle.appname, pysparkle.appver))
    dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
    dialog.exec_()


def update_available(pysparkle, maxitem, items):
    dialog = QtWidgets.QMessageBox()
    dialog.setIcon(QtWidgets.QMessageBox.Information)
    dialog.setWindowTitle(dialog.tr("A new version of {} is available!").format(pysparkle.appname))
    dialog.setText(dialog.tr("{} {} is now available (you have {}).\n\nWould you like to download it now?")
                   .format(pysparkle.appname, maxitem['version'], pysparkle.appver))
    if any(item['notes'] for item in items):
        grid = dialog.layout()
        label = QtWidgets.QLabel(dialog.tr("Release notes:"))
        grid.addWidget(label, grid.rowCount(), 0, 1, grid.columnCount())
        notes = QtWidgets.QTextEdit()
        notes.setText("<br/>\n".join("<h3>{title}</h3>\n{notes}\n".format(**item) for item in items))
        notes.setFixedHeight(200)
        notes.setReadOnly(True)
        grid.addWidget(notes, grid.rowCount(), 0, 1, grid.columnCount())
        dialog.updateGeometry()
    get_button = dialog.addButton(dialog.tr("Get update"), QtWidgets.QMessageBox.YesRole)
    skip_button = dialog.addButton(dialog.tr("Skip this version"), QtWidgets.QMessageBox.NoRole)
    later_button = dialog.addButton(dialog.tr("Remind me later"), QtWidgets.QMessageBox.RejectRole)
    dialog.exec_()
    result = dialog.clickedButton()
    if result in (get_button, skip_button):
        return result == get_button
