# Copyright (c) 2015-2016 Maciej Dems <maciej.dems@p.lodz.pl>
# See LICENSE file for copyright information.

import sys

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree
NS = '{http://www.andymatuschak.org/xml-namespaces/sparkle}'

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen


import platform
OS, _, _, _, ARCH, _ = platform.uname()
OS = OS.lower()
ARCH = ARCH.lower()
ARCH = {'amd64': 'x86_64'}.get(ARCH, ARCH)
if OS == 'linux':
    from .. import distro
    _dist, _dist_ver, _dist_id = (s.lower() for s in distro.linux_distribution(False))
    DISTS = [_dist]
    _dist += '-'
    _parts = _dist_ver.split('.')
    _partial_ver = _dist + _parts[0]
    DISTS.append(_partial_ver)
    for _part in _parts[1:]:
        _partial_ver = '.'.join((_partial_ver, _part))
        DISTS.append(_partial_ver)
    if _dist_id:
        DISTS.append(_dist+_dist_id)
else:
    python_version = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)
    DISTS = ['py'+python_version, 'python-'+python_version]


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
                        notes_link = item.findtext(NS+'releaseNotesLink')
                        if notes_link is not None:
                            try: notes = urlopen(notes_link, timeout=self.pysparkle.timeout).read()
                            except: pass
                    info['notes'] = notes.strip()
                enclosures = item.findall('enclosure')
                if enclosures:
                    os_matched = False
                    for enclosure in enclosures:
                        try:
                            encl = {
                                'url': enclosure.attrib['url'],
                                'ver': enclosure.attrib[NS+'version'],
                                'signature': enclosure.attrib.get(NS+'dsaSignature'),
                                'length': enclosure.attrib.get('length', 0)
                            }
                            encl['version'] = enclosure.attrib.get(NS+'shortVersionString', encl['ver'])
                            os = enclosure.attrib.get(NS+'os')
                            if os is not None:
                                try:
                                    os, arch = os.split('-')
                                except TypeError:
                                    if os_matched:
                                        # prefer enclosure with specified os and arch over a generic one
                                        continue
                                else:
                                    arch = {'x64': 'x86_64', 'x86': 'i386'}.get(arch, arch)
                                    if arch != ARCH:
                                        raise ValueError('arch='+arch)
                                if os != OS:
                                    raise ValueError('os='+os)
                                dist = enclosure.attrib.get(NS+'dist')
                                if dist is not None:
                                    if dist not in DISTS:
                                        raise ValueError('dist='+dist)
                                elif os_matched:
                                    # prefer enclosure with specified dist over a generic one
                                    continue
                                os_matched = True
                            elif os_matched:
                                # prefer enclosure with specified os over a generic one
                                continue
                        except (KeyError, ValueError):
                            continue
                        else:
                            info.update(encl)
                if 'url' not in info:
                    # did not find proper enclosure
                    link = item.findtext('link')
                    ver = item.findtext(NS+'version')
                    if link is not None and ver is not None:
                        info['link'] = link
                        info['ver'] = ver
                        info['url'] = None
                        info['version'] = item.findtext(NS+'shortVersionString', info['ver'])
                    else:
                        continue
                if 'ver' in info:
                    items.append(info)

        return items
