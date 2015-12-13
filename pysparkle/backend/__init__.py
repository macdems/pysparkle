# Copyright (c) 2015-2016 Maciej Dems <maciej.dems@p.lodz.pl>
# See LICENSE file for copyright information.

try:
    from urllib2 import urlopen, URLError, HTTPBasicAuthHandler, build_opener, install_opener
except ImportError:
    from urllib.request import urlopen, HTTPBasicAuthHandler, build_opener, install_opener
    from urllib.error import URLError
import socket

import locale
_,  _coding = locale.getdefaultlocale()


class PySparkleError(Exception):
    """
    Base class for PySparkle errors.
    """

    def __init__(self, message):
        try:
            self.message = unicode(message, _coding)
        except NameError:
            self.message = message


class ConnectionError(PySparkleError):
    """
    Error class raised when there is an internet connection error.
    """

    def __init__(self, url, message):
        super(ConnectionError, self).__init__(url + "\n\n" + message)


class PySparkleBackend(object):
    """
    PySparkle backend base class. It is responsible for downloading update data. Subclasses should overwrite
    methods that parse it.

    :param url: URL to download
    """

    def __init__(self, url, pysparkle):
        self.url = url
        self.pysparkle = pysparkle
        auth_user = pysparkle.config.get('auth_user')
        if auth_user is not None:
            auth_pass = pysparkle.config.get('auth_password', '')
            auth_handler = HTTPBasicAuthHandler()
            auth_handler.add_password(None, url, auth_user, auth_pass)
            opener = build_opener(auth_handler)
            install_opener(opener)

    def check_update(self, get_notes):
        """
        Download update info and parse its data.

        :param get_notes: Flag indicating if release notes should be retrieved.
        """

        try:
            handler = urlopen(self.url, timeout=self.pysparkle.timeout)
        except (URLError, socket.timeout) as err:
            raise ConnectionError(self.url, str(err))
        else:
            # print(handler.getcode())
            # print(handler.headers.getheader('content-type'))
            return self.parse_update_data(handler, get_notes)

    def parse_update_data(self, handler, get_notes):
        """
        Parse downloaded update data

        :param handler: urllib handler or file-like object to read update data from
        :param get_notes: Flag indicating if release notes should be retrieved.
        :return: parsed data
        """
        pass
