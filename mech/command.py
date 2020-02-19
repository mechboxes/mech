# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 German Mendez Bravo (Kronuz)
# Copyright (c) 2020 Mike Kinney
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
"""Handle the mech options using docopt."""

from __future__ import absolute_import

import re
import textwrap

import docopt

from .compat import get_meth_func


NBSP = '__'


def cmd_usage(doc):
    """Show the command usage."""
    return doc.replace(NBSP, ' ')


docopt_extras_ref = docopt.extras


def docopt_extras(the_help, version, options, doc):
    """Show the "Extra" help info."""
    return docopt_extras_ref(the_help, version, options, cmd_usage(doc))


def DocoptExit____init__(self, message=''):
    """Constructor for docopt."""
    SystemExit.__init__(self, (message + '\n' + cmd_usage(self.usage)).strip())


docopt.extras = docopt_extras
docopt.DocoptExit.__init__ = DocoptExit____init__


def spaced(name):
    """Return the command name."""
    name = re.sub(r'[ _]+', r' ', name)
    name = re.sub(r'(?<=[^_])([A-Z])', r' \1', name).lower()
    return re.sub(r'^( *)(.*?)( *)$', r'\2', name)


class Command():
    """
    Usage: command <subcommand> [<args>...]
    """

    subcommand_name = '<subcommand>'
    argv_name = '<args>'

    @staticmethod
    def docopt(doc, **kwargs):
        """Parse comments for arguments."""
        name = kwargs.pop('name', "")
        name = spaced(name)
        doc = textwrap.dedent(doc).replace(name, name.replace(' ', NBSP))
        arguments = docopt.docopt(doc, options_first=True, **kwargs)
        return arguments

    def __init__(self, arguments):
        self.arguments = arguments

    def __call__(self):
        """Invoke the command with the arguments."""
        if self.subcommand_name in self.arguments:
            cmd = self.arguments[self.subcommand_name]
            cmd_attr = cmd.replace('-', '_')
            if hasattr(self, cmd_attr):
                klass = getattr(self, cmd_attr)
                meth_func = get_meth_func(klass)
                if meth_func:
                    cmd = meth_func.__name__.replace('_', '-')
                name = '{} {}'.format(self.__class__.__name__, cmd)
                if klass.__doc__:
                    arguments = self.docopt(klass.__doc__,
                                            argv=self.arguments.get(self.argv_name, []), name=name)
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
        """Run the command."""
        raise docopt.DocoptExit()
