# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 German Mendez Bravo (Kronuz)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

import re
import textwrap

import docopt


NBSP = '\xc2\xa0'


def spaced(name):
    name = re.sub(r'[ _]+', r' ', name)
    name = re.sub(r'(?<=[^_])([A-Z])', r' \1', name).lower()
    return re.sub(r'^( *)(.*?)( *)$', r'\2', name)


class Command(object):
    """
    Usage: command <subcommand> [<args>...]
    """

    subcommand_name = '<subcommand>'
    argv_name = '<args>'

    @staticmethod
    def docopt(doc, **kwargs):
        name = kwargs.pop('name', "")
        name = spaced(name)
        doc = textwrap.dedent(doc).replace(name, name.replace(' ', NBSP))
        arguments = docopt.docopt(doc, options_first=True, **kwargs)
        return arguments

    def __init__(self, arguments):
        self.arguments = arguments

    def __call__(self):
        if self.subcommand_name in self.arguments:
            cmd = self.arguments[self.subcommand_name]
            cmd_attr = cmd.replace('-', '_')
            if hasattr(self, cmd_attr):
                klass = getattr(self, cmd_attr)
                if hasattr(klass, 'im_func'):
                    cmd = klass.im_func.__name__.replace('_', '-')
                name = '{} {}'.format(self.__class__.__name__, cmd)
                if klass.__doc__:
                    arguments = self.docopt(klass.__doc__, argv=self.arguments.get(self.argv_name, []), name=name)
                else:
                    arguments = []
                obj = klass(arguments)
            else:
                obj = self.run()
        else:
            obj = self.run()
        if callable(obj):
            obj = obj()
        return obj

    def run(self):
        raise docopt.DocoptExit()
