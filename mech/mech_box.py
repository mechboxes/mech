# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017 Kevin Chung
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
"""MechBox class"""

from __future__ import print_function, absolute_import

import os
import fnmatch
import logging
import shutil

from . import utils
from .mech_command import MechCommand

LOGGER = logging.getLogger(__name__)


class MechBox(MechCommand):
    """
    Usage: mech box <subcommand> [<args>...]

    Available subcommands:
        add               add a box to the catalog of available boxes
        (list|ls)         list available boxes in the catalog
        (remove|delete)   removes a box that matches the given name

    For help on any individual subcommand run `mech box <subcommand> -h`
    """

    def add(self, arguments):  # pylint: disable=no-self-use
        """
        Add a box to the catalog of available boxes.

        Usage: mech box add [options] <location>

        Notes:
            The location can be a:
                URL (ex: 'http://example.com/foo.box'),
                box file (ex: 'file:/mnt/boxen/foo.box'),
                json file (ex: 'file:/tmp/foo.json'), or
                HashiCorp account/box (ex: 'bento/ubuntu-18.04').

        Options:
                --box-version VERSION        Constrain version of the added box
            -f, --force                      Overwrite an existing box if it exists
            -h, --help                       Print this help
        """

        location = arguments['<location>']
        box_version = arguments['--box-version']

        force = arguments['--force']
        utils.add_box(name=None, box=None, location=location, box_version=box_version,
                      force=force)

    def list(self, arguments):  # pylint: disable=no-self-use,unused-argument
        """
        List all available boxes in the catalog.

        Usage: mech box list [options]

        Options:
            -h, --help                       Print this help
        """

        print("{}\t{}".format(
            'BOX'.rjust(35),
            'VERSION'.rjust(12),
        ))
        path = os.path.abspath(os.path.join(utils.mech_dir(), 'boxes'))
        for root, _, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, '*.box'):
                directory = os.path.dirname(os.path.join(root, filename))[len(path) + 1:]
                account, box, version = (directory.split('/', 2) + ['', ''])[:3]
                print("{}\t{}".format(
                    "{}/{}".format(account, box).rjust(35),
                    version.rjust(12),
                ))

    # add alias for 'mech box ls'
    ls = list

    def remove(self, arguments):  # pylint: disable=no-self-use
        """
        Remove a box from mech that matches the given name and version.

        Usage: mech box remove [options] <name> <version>

        Options:
            -h, --help                       Print this help
        """
        name = arguments['<name>']
        box_version = arguments['<version>']
        path = os.path.abspath(os.path.join(utils.mech_dir(), 'boxes', name, box_version))
        if os.path.exists(path):
            shutil.rmtree(path)
            print("Removed {} {}".format(name, box_version))
        else:
            print("No boxes were removed.")

    # add alias for 'mech box delete'
    delete = remove
