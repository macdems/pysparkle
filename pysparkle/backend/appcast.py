# Copyright (c) 2015-2016 Maciej Dems <maciej.dems@p.lodz.pl>
# See LICENSE file for copyright information.

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree
ElementTree.register_namespace('sparkle', 'http://www.andymatuschak.org/xml-namespaces/sparkle')
NS = '{http://www.andymatuschak.org/xml-namespaces/sparkle}'

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from .import PySparkleBackend


class Appcast(PySparkleBackend):
    """
    Appcast parser class. It is responsible for downloading appcasts and parsing its XML contents.

    :param url: Appcast url to download
    """

    def parse_update_data(self, handler, get_notes):
        tree = ElementTree.parse(handler)
        rss = tree.getroot()
        items = []
        for channel in rss.iter('channel'):
            for item in channel.findall('item'):
                info = {'title': item.findtext('title', '')}
                if get_notes:
                    notes = item.findtext('description')
                    if notes is None:
                        notes = ''
                        notes_link = item.findtext('sparkle:releaseNotesLink')
                        if notes_link is not None:
                            try: notes = urlopen(notes_link, timeout=self.pysparkle.timeout).read()
                            except: pass
                    info['notes'] = notes.strip()
                enclosure = item.find('enclosure')
                if enclosure is not None:
                    try:
                        info['url'] = enclosure.attrib['url']
                        info['ver'] = enclosure.attrib[NS+'version']
                    except KeyError:
                        continue
                    else:
                        info['version'] = enclosure.get(NS+'shortVersionString', info['ver'])
                        info['signature'] = enclosure.get(NS+'dsaSignature')
                        info['length'] = enclosure.get('length', 0)
                        os = enclosure.get(NS+'os')
                        if os is not None:
                            try:
                                os, arch = os.split('-')
                            except TypeError:
                                arch = None
                            else:
                                arch = {'x64': 'x86_64', 'x86': 'i386'}.get(arch, arch)
                            info['os'] = os
                            info['arch'] = arch
                        info['dist'] = enclosure.get(NS+'dist')
                else:
                    try:
                        info['link'] = item.attrib['link']
                        info['ver'] = item.attrib[NS+'version']
                    except KeyError:
                        continue
                    else:
                        info['url'] = None
                        info['version'] = item.get(NS+'shortVersionString', info['ver'])

                items.append(info)

        return items