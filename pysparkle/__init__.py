# Copyright (c) 2015-2016 Maciej Dems <maciej.dems@p.lodz.pl>
# See LICENSE file for copyright information.

import sys
import os
import shlex
import importlib
import webbrowser
import tempfile

try:
    from urllib2 import urlretrieve
except ImportError:
    from urllib.request import urlretrieve

from .backend import ConnectionError
from .backend.appcast import Appcast

try:
    unicode = unicode
except NameError:
    unicode = str


class _DebugDict(dict):
    def sync(self):
        print(self)


class PySparkle(object):
    """
    Main PySparkle class.

    You should create an instance of this class in your application if you want to use PySparkle.
    Normally you would do so at application startup and store it, so the user can check for
    update manually.

    :param url: Appcast URL for your application.
    :param appname: Application name to display in a window.
    :param appver: Current application version.
    :param frontend: String containing frontend name. Currently only 'qt' is implemented.
    :param config: Dict-like object storing both the PySparkle configuration as well as its internal state.
                   It should be a persistent dict, e.g. provided by a shelve module, or QSettings proxy.
                   After PySparkle writes anything to this dict it tries to call its 'sync' method, in which
                   you should implement permanently storing the dictionary.
    :param timeout: Allowed connection timeout.
    :param show_notes: Flag indicating if release notes should be shown for newer versions.
    :param shutdown: Boolean indicating whether the application needs to be shutdown for upgrade or a callable
                     returning such Boolean value. The callable must not close the application itself, but it
                     should return `True` if the application can be shut down. PySparkle will issue ``os.execv(...)``
                     to close the application and launch the installer.
    """
    def __init__(self, url, appname, appver, frontend='qt', config=_DebugDict(), timeout=3, show_notes=False, shutdown=True):
        self.appname = appname
        self.skipver = config.get('skip_version')
        self.appver = appver
        self.config = config
        if self.skipver is not None:
            if self.skipver < self.appver:
                config['skip_version'] = self.skipver = None
                try:
                    config.sync()
                except AttributeError:
                    pass
        self.timeout = timeout
        self.show_notes = show_notes
        self.shutdown = shutdown
        self.frontend = importlib.import_module('.frontend.' + frontend, __name__)
        self.backend = Appcast(url, self)
        auto_check = self.config.get('automatic_check')
        if auto_check is None:
            auto_check = self.ask_for_autocheck()
        if auto_check:
            self.check_update(verbose=False)

    def ask_for_autocheck(self):
        """
        Ask user if PySparkle should automatically check for updates and store the answer in the config.
        :return: True if user allowed for automatic check
        """
        answer = self.frontend.ask_for_autocheck(self)
        self.config['automatic_check'] = answer
        try:
            self.config.sync()
        except AttributeError:
            pass
        return answer

    def check_update(self, verbose=True, force=False):
        """
        Check for update. If new version is found, a dialog is displayed with its summary. User can then
        either download (and install) the new version, skip the current version or close the dialog allowing
        further notification.

        :param verbose: If this flag is set to True, the info is displayed on errors and in case there is no update.
                        Otherwise errors and no-updates are silently ignored.
        :param force: If this flag is set to True, last skipped version is ignored as if it were never set.
        :return:
        """
        try:
            items = self.backend.check_update(self.show_notes)
        except Exception as err:
            if verbose: self.frontend.update_error(unicode(err))
        else:
            if items is None:
                if verbose: self.frontend.update_error(self)
                return
            elif not items:
                if verbose: self.frontend.no_info(self)
                return
            # Filter by current os, architecture, and distribution
            appver = self.appver if (force or self.skipver is None) else self.skipver
            maxitem = max((item for item in items), key=lambda item: item['ver'])
            if appver >= maxitem['ver']:
                if verbose: self.frontend.no_update(self)
                return
            notes = [item for item in items if item['ver'] >= self.appver] if self.show_notes else []
            answer = self.frontend.update_available(self, maxitem, notes)
            if answer is not None:
                if answer:
                    url = maxitem['url']
                    if url is None: url = maxitem['link']
                    install = maxitem.get('install')
                    if self.shutdown is False:
                        install = None
                    if install is not None:
                        filename = os.path.join(tempfile.gettempdir(), os.path.basename(url))
                        try:
                            filename, headers = urlretrieve(url, filename)
                            install = install.format(file=filename)
                            install_args = [s for s in shlex.split(install)]
                            if self.shutdown is True or self.shutdown():
                                if os.name == 'nt':
                                    try:
                                        os.execvp(install_args[0], install_args)
                                    except OSError:
                                        # This error may happen because the installer is run with elevated privileges
                                        try:
                                            import win32com.client
                                        except (ModuleNotFoundError, ImportError):
                                            batch_handle, batch_filename = tempfile.mkstemp(suffix='.cmd')
                                            with os.fdopen(batch_handle, "w") as batch_file:
                                                print('@echo off\nstart %*\n(goto) 2>nul & del "%~f0"', file=batch_file)
                                            os.execv(batch_filename, [batch_filename] + install_args)
                                        else:
                                            shell = win32com.client.Dispatch("WScript.Shell")
                                            try:
                                                shell.Run(install)
                                            except:
                                                sys.exit(127)
                                            else:
                                                sys.exit(0)
                                else:
                                    os.execvp(install_args[0], install_args)
                        except Exception:
                            try:
                                os.remove(filename)
                            except:
                                pass
                    webbrowser.open(url, autoraise=True)
                    if self.shutdown is True or (self.shutdown is not False and self.shutdown()):
                        sys.exit(0)
                else:
                    self.config['skip_version'] = self.skipver = maxitem['ver']
                    try:
                        self.config.sync()
                    except AttributeError:
                        pass


__all__ = ['PySparkle']
