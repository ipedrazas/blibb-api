
from __future__ import print_function
from __future__ import unicode_literals

import sys
from io import StringIO


class blibb2rss:
    def __init__(self, dict):
        self.title = ""
        self.version = "0.2"
        self.link = ""
        self.date = ""
        self.description = "a mapped dict2rss"
        self.itemio = StringIO()

        blibb = dict['blibb']
        items = dict['items']

        for key in blibb:
            element = blibb[key]
            if key == 'name':
                self.title = element
            elif key == 'description':
                self.description = element
            elif key == 'url':
                self.link = element
            elif key == 'date':
                self.date = element

            sys.stdout = self.itemio

        for item in items:
            print(u'\t\t<item>')
            for element in item['i']:
                # print(u'\t\t\t' + '<' + str(element['s']) + ' label="\>' + str(element['v']) + '</' + str(element['s']) + '>')
                line = '\t\t\t<%(s)s><label>%(l)s</label><value>%(v)s</value></%(s)s>' % element
                print(line)
            print(u'\t\t</item>')

        sys.stdout = sys.__stdout__

    def PrettyPrint(self):
        print(self._out())

    def Print(self):
        print(self._out().replace("\t", ""))

    def TinyPrint(self):
        print(self._out().replace("\t", "").replace("\n", ""))

    def output(self):
        return self._out()

    def _out(self):
        d = u'<?xml version="1.0" encoding="UTF-8"?>\n\n'
        d += '<blibb>\n'
        d += ('\t<title>%s</title>\n' % self.title)
        d += ('\t<link>%s</link>\n' % self.link)
        d += ('\t<description>%s</description>\n' % self.description)
        d += ('\t<date>%s</date>\n' % self.date)
        d += self.itemio.getvalue()
        d += '</blibb>\n'
        return d.encode('utf-8')
