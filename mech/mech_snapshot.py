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
"""MechSnapshot class"""

from __future__ import print_function, absolute_import

import sys
import logging

from clint.textui import colored

from .vmrun import VMrun
from .mech_instance import MechInstance
from .mech_command import MechCommand

LOGGER = logging.getLogger(__name__)


class MechSnapshot(MechCommand):
    """
    Usage: mech snapshot <subcommand> [<args>...]

    Available subcommands:
        (delete|remove)   delete a snapshot taken previously with snapshot save
        (list|ls)         list all snapshots taken for a machine
        save              take a snapshot of the current state of the machine

    For help on any individual subcommand run `mech snapshot <subcommand> -h`
    """

    def delete(self, arguments):  # pylint: disable=no-self-use
        """
        Delete a snapshot taken previously with snapshot save.

        Usage: mech snapshot delete [options] <name> <instance>

        Options:
            -h, --help                       Print this help
        """
        name = arguments['<name>']

        instance = arguments['<instance>']
        inst = MechInstance(instance)

        vmrun = VMrun(inst.vmx)
        if vmrun.delete_snapshot(name) is None:
            print(colored.red("Cannot delete name"))
        else:
            print(colored.green("Snapshot {} deleted".format(name)))

    # add alias for 'mech snapshot remove'
    remove = delete

    def list(self, arguments):
        """
        List all snapshots taken for a machine.

        Usage: mech snapshot list [options] [<instance>]

        Options:
            -h, --help                       Print this help
        """
        instance_name = arguments['<instance>']

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)
            print('Snapshots for instance:{}'.format(instance))
            if inst.created:
                vmrun = VMrun(inst.vmx)
                print(vmrun.list_snapshots())
            else:
                print(colored.red('Instance ({}) is not created.'.format(instance)))

    # add alias for 'mech snapshot ls'
    ls = list

    def save(self, arguments):  # pylint: disable=no-self-use
        """
        Take a snapshot of the current state of the machine.

        Usage: mech snapshot save [options] <name> <instance>

        Notes:
            Take a snapshot of the current state of the machine.

            Snapshots are useful for experimenting in a machine and being able
            to rollback quickly.

        Options:
            -h, --help                       Print this help
        """
        name = arguments['<name>']
        instance = arguments['<instance>']

        inst = MechInstance(instance)
        if inst.created:
            vmrun = VMrun(inst.vmx)
            if vmrun.snapshot(name) is None:
                sys.exit(colored.red("Warning: Could not take snapshot."))
            else:
                print(colored.green("Snapshot ({}) on VM ({}) taken".format(name, instance)))
        else:
            print(colored.red('Instance ({}) is not created.'.format(instance)))
