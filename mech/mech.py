# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017 Kevin Chung
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
"""Mech classes."""

from __future__ import print_function, absolute_import

import os
import re
import sys
import fnmatch
import logging
import tempfile
import textwrap
import shutil
import subprocess

from clint.textui import colored

from . import utils
from .vmrun import VMrun
from .command import Command

LOGGER = logging.getLogger(__name__)

DEFAULT_USER = 'vagrant'
DEFAULT_PASSWORD = 'vagrant'
INSECURE_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEA6NF8iallvQVp22WDkTkyrtvp9eWW6A8YVr+kz4TjGYe7gHzI
w+niNltGEFHzD8+v1I2YJ6oXevct1YeS0o9HZyN1Q9qgCgzUFtdOKLv6IedplqoP
kcmF0aYet2PkEDo3MlTBckFXPITAMzF8dJSIFo9D8HfdOV0IAdx4O7PtixWKn5y2
hMNG0zQPyUecp4pzC6kivAIhyfHilFR61RGL+GPXQ2MWZWFYbAGjyiYJnAmCP3NO
Td0jMZEnDkbUvxhMmBYSdETk1rRgm+R4LOzFUGaHqHDLKLX+FIPKcF96hrucXzcW
yLbIbEgE98OHlnVYCzRdK8jlqm8tehUc9c9WhQIBIwKCAQEA4iqWPJXtzZA68mKd
ELs4jJsdyky+ewdZeNds5tjcnHU5zUYE25K+ffJED9qUWICcLZDc81TGWjHyAqD1
Bw7XpgUwFgeUJwUlzQurAv+/ySnxiwuaGJfhFM1CaQHzfXphgVml+fZUvnJUTvzf
TK2Lg6EdbUE9TarUlBf/xPfuEhMSlIE5keb/Zz3/LUlRg8yDqz5w+QWVJ4utnKnK
iqwZN0mwpwU7YSyJhlT4YV1F3n4YjLswM5wJs2oqm0jssQu/BT0tyEXNDYBLEF4A
sClaWuSJ2kjq7KhrrYXzagqhnSei9ODYFShJu8UWVec3Ihb5ZXlzO6vdNQ1J9Xsf
4m+2ywKBgQD6qFxx/Rv9CNN96l/4rb14HKirC2o/orApiHmHDsURs5rUKDx0f9iP
cXN7S1uePXuJRK/5hsubaOCx3Owd2u9gD6Oq0CsMkE4CUSiJcYrMANtx54cGH7Rk
EjFZxK8xAv1ldELEyxrFqkbE4BKd8QOt414qjvTGyAK+OLD3M2QdCQKBgQDtx8pN
CAxR7yhHbIWT1AH66+XWN8bXq7l3RO/ukeaci98JfkbkxURZhtxV/HHuvUhnPLdX
3TwygPBYZFNo4pzVEhzWoTtnEtrFueKxyc3+LjZpuo+mBlQ6ORtfgkr9gBVphXZG
YEzkCD3lVdl8L4cw9BVpKrJCs1c5taGjDgdInQKBgHm/fVvv96bJxc9x1tffXAcj
3OVdUN0UgXNCSaf/3A/phbeBQe9xS+3mpc4r6qvx+iy69mNBeNZ0xOitIjpjBo2+
dBEjSBwLk5q5tJqHmy/jKMJL4n9ROlx93XS+njxgibTvU6Fp9w+NOFD/HvxB3Tcz
6+jJF85D5BNAG3DBMKBjAoGBAOAxZvgsKN+JuENXsST7F89Tck2iTcQIT8g5rwWC
P9Vt74yboe2kDT531w8+egz7nAmRBKNM751U/95P9t88EDacDI/Z2OwnuFQHCPDF
llYOUI+SpLJ6/vURRbHSnnn8a/XG+nzedGH5JGqEJNQsz+xT2axM0/W/CRknmGaJ
kda/AoGANWrLCz708y7VYgAtW2Uf1DPOIYMdvo6fxIB5i9ZfISgcJ/bbCUkFrhoH
+vq/5CIWxCPp0f85R4qxxQ5ihxJ0YDQT9Jpx4TMss4PSavPaBH3RXow5Ohe+bYoQ
NE5OgEXk2wVfZczCZpigBKbKZHNYcelXtTt/nP3rsCuGcM4h53s=
-----END RSA PRIVATE KEY-----
"""


class MechInstance():
    """Class to hold a mech instance (aka virtual machine)."""

    def __init__(self, name, mechfile=None):
        """Constructor for the mech instance."""
        if not name or name == "":
            raise AttributeError("Must provide a name for the instance.")
        if not mechfile:
            mechfile = utils.load_mechfile()
        LOGGER.debug("loaded mechfile:%s", mechfile)
        if mechfile.get(name, None):
            self.name = name
        else:
            sys.exit(colored.red("Instance ({}) was not found in the "
                                 "Mechfile".format(name)))
        self.box = mechfile[name].get('box', None)
        self.box_version = mechfile[name].get('box_version', None)
        self.url = mechfile[name].get('url', None)
        self.box_file = mechfile[name].get('file', None)
        self.provision = mechfile[name].get('provision', None)
        self.enable_ip_lookup = False
        self.config = {}
        self.user = DEFAULT_USER
        self.password = DEFAULT_PASSWORD
        self.path = os.path.join(utils.mech_dir(), name)
        vmx = utils.locate(self.path, '*.vmx')
        # Note: If vm has not been started vmx will be None
        if vmx:
            self.vmx = vmx
            self.created = True
        else:
            self.vmx = None
            self.created = False

    def __repr__(self):
        """Return a representation of a Mech instance."""
        sep = '\n'
        return ('name:{name}{sep}created:{created}{sep}box:{box}{sep}'
                'box_version:{box_version}{sep}'
                'url:{url}{sep}box_file:{box_file}{sep}provision:{provision}{sep}'
                'vmx:{vmx}{sep}user:{user}{sep}'
                'password:{password}{sep}enable_ip_lookup:{enable_ip_lookup}'
                '{sep}config:{config}'.
                format(name=self.name, created=self.created, box=self.box,
                       box_version=self.box_version, url=self.url,
                       box_file=self.box_file, provision=self.provision,
                       vmx=self.vmx, user=self.user, password=self.password,
                       enable_ip_lookup=self.enable_ip_lookup, config=self.config,
                       sep=sep))

    def config_ssh(self):
        """Configure ssh to work. Create a insecure private key file for ssh/scp."""
        vmrun = VMrun(self.vmx, user=self.user, password=self.password)
        lookup = self.enable_ip_lookup
        ip_address = vmrun.get_guest_ip_address(wait=False,
                                                lookup=lookup) if vmrun.installed_tools() else None
        if not ip_address:
            sys.exit(colored.red(textwrap.fill(
                     "This Mech machine is reporting that it is not yet ready for SSH. "
                     "Make sure your machine is created and running and try again. "
                     "Additionally, check the output of `mech status` to verify "
                     "that the machine is in the state that you expect.")))

        insecure_private_key = os.path.abspath(os.path.join(
            utils.mech_dir(), "insecure_private_key"))
        if not os.path.exists(insecure_private_key):
            with open(insecure_private_key, 'w') as the_file:
                the_file.write(INSECURE_PRIVATE_KEY)
            os.chmod(insecure_private_key, 0o400)
        self.config = {
            "Host": self.name,
            "User": self.user,
            "Port": "22",
            "UserKnownHostsFile": "/dev/null",
            "StrictHostKeyChecking": "no",
            "PasswordAuthentication": "no",
            "IdentityFile": insecure_private_key,
            "IdentitiesOnly": "yes",
            "LogLevel": "FATAL",
        }
        for key, value in self.config.items():
            key = re.sub(r'[ _]+', r' ', key)
            key = re.sub(r'(?<=[^_])([A-Z])', r' \1', key).lower()
            key = re.sub(r'^( *)(.*?)( *)$', r'\2', key)

            def callback(pat):
                return pat.group(1).upper()

            key = re.sub(r' (\w)', callback, key)
            if key[0].islower():
                key = key[0].upper() + key[1:]
            self.config[key] = value
        self.config.update({
            "HostName": ip_address,
        })
        return self.config


class MechCommand(Command):
    """Class for the mech commands from help doc (as python object)."""
    mechfile = None

    def activate_mechfile(self):
        """Load the Mechfile."""
        self.mechfile = utils.load_mechfile()
        LOGGER.debug("loaded mechfile:%s", self.mechfile)

    def instances(self):
        """Returns a list of the instances from the Mechfile."""
        if not self.mechfile:
            self.activate_mechfile()
        return list(self.mechfile)


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
                .box file (ex: 'file:/mnt/boxen/foo.box'),
                .json file (ex: 'file:/tmp/foo.json'), or
                HashiCorp account/box (ex: 'bento/ubuntu-18.04').

        Options:
            -f, --force                      Overwrite an existing box if it exists
                --insecure                   Do not validate SSL certificates
                --cacert FILE                CA certificate for SSL download
                --capath DIR                 CA certificate directory for SSL download
                --cert FILE                  A client SSL cert, if needed
                --box-version VERSION        Constrain version of the added box
                --checksum CHECKSUM          Checksum for the box
                --checksum-type TYPE         Checksum type (md5, sha1, sha256)
            -h, --help                       Print this help
        """

        location = arguments['<location>']
        box_version = arguments['--box-version']

        force = arguments['--force']
        requests_kwargs = utils.get_requests_kwargs(arguments)
        utils.add_box(name=None, box=None, location=location, box_version=box_version,
                      force=force, requests_kwargs=requests_kwargs)

    def list(self, arguments):  # pylint: disable=no-self-use
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

        vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)
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
                vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)
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
            vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)
            if vmrun.snapshot(name) is None:
                sys.exit(colored.red("Warning: Could not take snapshot."))
            else:
                print(colored.green("Snapshot ({}) on VM ({}) taken".format(name, instance)))
        else:
            print(colored.red('Instance ({}) is not created.'.format(instance)))


class Mech(MechCommand):
    """
    Usage: mech [options] <command> [<args>...]

    Options:
        -v, --version                    Print the version and exit.
        -h, --help                       Print this help.
        --debug                          Show debug messages.

    Common commands:
        (list|ls)         lists all available boxes
        init              initializes a new Mech environment by creating a Mechfile
        destroy           stops and deletes all traces of the instances
        (up|start)        starts instances (aka virtual machines)
        (down|stop|halt)  stops the instances
        suspend           suspends the instances
        pause             pauses the instances
        ssh               connects to an instance via SSH
        ssh-config        outputs OpenSSH valid configuration to connect to the instances
        scp               copies files to/from the machine via SCP
        ip                outputs ip of an instance
        box               manages boxes: add, list remove, etc.
        global-status     outputs status of all virutal machines on this host
        status            outputs status of the instances
        ps                list running processes for an instance
        provision         provisions the Mech machine
        reload            restarts Mech machine, loads new Mechfile configuration
        resume            resume a paused/suspended Mech machine
        snapshot          manages snapshots: save, list, remove, etc.
        port              displays information about guest port mappings

    For help on any individual command run `mech <command> -h`

    All "state" will be saved in .mech directory. (boxes and instances)

    Example:

    Initializing and using a machine from HashiCorp's Vagrant Cloud:

        mech init bento/ubuntu-18.04
        mech up
        mech ssh
    """

    subcommand_name = '<command>'

    def __init__(self, arguments):
        super(Mech, self).__init__(arguments)

        logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter('%(filename)s:%(lineno)s %(funcName)s() '
                                      '%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        if arguments['--debug']:
            logger.setLevel(logging.DEBUG)

    box = MechBox
    snapshot = MechSnapshot

    def init(self, arguments):  # pylint: disable=no-self-use
        """
        Initializes a new mech environment by creating a Mechfile.

        Usage: mech init [options] <location>

        Notes:
            The location can be a:
                URL (ex: 'http://example.com/foo.box'),
                .box file (ex: 'file:/mnt/boxen/foo.box'),
                .json file (ex: 'file:/tmp/foo.json'), or
                HashiCorp account/box (ex: 'bento/ubuntu-18.04').

        Options:
            -f, --force                      Overwrite existing Mechfile
                --insecure                   Do not validate SSL certificates
                --cacert FILE                CA certificate for SSL download
                --capath DIR                 CA certificate directory for SSL download
                --cert FILE                  A client SSL cert, if needed
                --box-version VERSION        Constrain version of the added box
                --checksum CHECKSUM          Checksum for the box
                --checksum-type TYPE         Checksum type (md5, sha1, sha256)
                --name INSTANCE              Name of the instance (myinst1)
                --box BOXNAME                Name of the box (ex: bento/ubuntu-18.04)
            -h, --help                       Print this help
        """
        name = arguments['--name']
        box_version = arguments['--box-version']
        box = arguments['--box']
        location = arguments['<location>']

        if not name or name == "":
            name = "first"

        force = arguments['--force']
        requests_kwargs = utils.get_requests_kwargs(arguments)

        LOGGER.debug('name:%s box:%s box_version:%s location:%s', name, box, box_version, location)

        if os.path.exists('Mechfile') and not force:
            sys.exit(colored.red(textwrap.fill(
                     "`Mechfile` already exists in this directory. Remove it "
                     "before running `mech init`.")))

        print(colored.green("Initializing mech"))
        if utils.init_mechfile(
                location=location,
                box=box,
                name=name,
                box_version=box_version,
                requests_kwargs=requests_kwargs):
            print(colored.green(textwrap.fill(
                "A `Mechfile` has been initialized and placed in this directory. "
                "You are now ready to `mech up` your first virtual environment!"
            )))
        else:
            print(colored.red("Couldn't initialize mech"))

    def add(self, arguments):  # pylint: disable=no-self-use
        """
        Add instance to the Mechfile.

        Usage: mech add [options] <name> <location>

        Example box: bento/ubuntu-18.04

        Options:
                --insecure                   Do not validate SSL certificates
                --cacert FILE                CA certificate for SSL download
                --capath DIR                 CA certificate directory for SSL download
                --cert FILE                  A client SSL cert, if needed
                --box-version VERSION        Constrain version of the added box
                --checksum CHECKSUM          Checksum for the box
                --checksum-type TYPE         Checksum type (md5, sha1, sha256)
                --box BOXNAME                Name of the box (ex: bento/ubuntu-18.04)
            -h, --help                       Print this help
        """
        name = arguments['<name>']
        box_version = arguments['--box-version']
        box = arguments['--box']
        location = arguments['<location>']

        if not name or name == "":
            sys.exit(colored.red("Need to provide a name for the instance to add to the Mechfile."))

        requests_kwargs = utils.get_requests_kwargs(arguments)

        LOGGER.debug('name:%s box:%s box_version:%s location:%s', name, box, box_version, location)

        print(colored.green("Adding ({}) to the Mechfile.".format(name)))

        if utils.add_to_mechfile(
                location=location,
                box=box,
                name=name,
                box_version=box_version,
                requests_kwargs=requests_kwargs):
            print(colored.green("Added to the Mechfile."))
        else:
            print(colored.red("Could not add {} to the Mechfile".format(name)))

    def remove(self, arguments):
        """
        Remove instance from the Mechfile.

        Usage: mech remove [options] <name>

        Options:
            -h, --help                       Print this help
        """
        name = arguments['<name>']

        if not name or name == "":
            sys.exit(colored.red("Need to provide a name to be removed from the Mechfile."))

        LOGGER.debug('name:%s', name)

        self.activate_mechfile()
        inst = self.mechfile.get(name, None)
        if inst:
            print(colored.green("Removing ({}) from the Mechfile.".format(name)))
            if utils.remove_mechfile_entry(name=name):
                print(colored.green("Removed from the Mechfile."))
            else:
                print(colored.red("Could not remove {} from the Mechfile".format(name)))
        else:
            sys.exit(colored.red("There is no instance called ({}) in the Mechfile.".format(name)))

    # add alias for 'mech delete'
    delete = remove

    def up(self, arguments):  # pylint: disable=invalid-name
        """
        Starts and provisions the mech environment.

        Usage: mech up [options] [<instance>]

        Note: If no instance is specified, all instances will be started.

        Options:
                --gui                        Start GUI
                --disable-shared-folders     Do not share folders with VM
                --disable-provisioning       Do not provision
                --insecure                   Do not validate SSL certificates
                --cacert FILE                CA certificate for SSL download
                --capath DIR                 CA certificate directory for SSL download
                --cert FILE                  A client SSL cert, if needed
                --checksum CHECKSUM          Checksum for the box
                --checksum-type TYPE         Checksum type (md5, sha1, sha256)
                --no-cache                   Do not save the downloaded box
                --memsize 1024               Specify the size of memory for VM
                --numvcpus 1                 Specify the number of vcpus for VM
            -h, --help                       Print this help
        """
        gui = arguments['--gui']
        disable_shared_folders = arguments['--disable-shared-folders']
        disable_provisioning = arguments['--disable-provisioning']
        save = not arguments['--no-cache']
        requests_kwargs = utils.get_requests_kwargs(arguments)

        numvcpus = arguments['--numvcpus']
        memsize = arguments['--memsize']

        instance_name = arguments['<instance>']

        LOGGER.debug('gui:%s disable_shared_folders:%s disable_provisioning:%s '
                     'save:%s numvcpus:%s memsize:%s', gui, disable_shared_folders,
                     disable_provisioning, save, numvcpus, memsize)

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)

            location = inst.url
            if not location:
                location = inst.box_file

            vmx = utils.init_box(
                instance,
                box=inst.box,
                box_version=inst.box_version,
                location=location,
                instance_path=inst.path,
                requests_kwargs=requests_kwargs,
                save=save,
                numvcpus=numvcpus,
                memsize=memsize)
            if vmx:
                inst.vmx = vmx
                inst.created = True

            vmrun = VMrun(vmx, user=inst.user, password=inst.password)
            print(colored.blue("Bringing machine ({}) up...".format(instance)))
            started = vmrun.start(gui=gui)
            if started is None:
                print(colored.red("VM not started"))
            else:
                print(colored.blue("Getting IP address..."))
                lookup = inst.enable_ip_lookup
                ip_address = vmrun.get_guest_ip_address(lookup=lookup)
                if not disable_shared_folders:
                    print(colored.blue("Sharing current folder..."))
                    vmrun.enable_shared_folders(quiet=False)
                    vmrun.add_shared_folder('mech', utils.main_dir(), quiet=True)
                if ip_address:
                    if started:
                        print(colored.green("VM ({})"
                                            "started on {}".format(instance, ip_address)))
                    else:
                        print(colored.yellow("VM ({}) was already started "
                                             "on {}".format(instance, ip_address)))
                else:
                    if started:
                        print(colored.green("VM ({}) started on an unknown "
                                            "IP address".format(instance)))
                    else:
                        print(colored.yellow("VM ({}) was already started on an "
                                             "unknown IP address".format(instance)))
                if not disable_provisioning:
                    utils.provision(instance, inst.vmx, inst.user, inst.password,
                                    inst.provision, show=False)

    # allows "mech start" to alias to "mech up"
    start = up

    def global_status(self, arguments):  # pylint: disable=no-self-use
        """
        Outputs info about all VMs running on this computer.

        Usage: mech global-status [options]

        Options:
            -h, --help                       Print this help
        """
        vmrun = VMrun()
        print(vmrun.list())

    def ps(self, arguments):  # pylint: disable=invalid-name,no-self-use
        """
        List running processes in Guest OS.

        Usage: mech ps [options] <instance>

        Options:
            -h, --help                       Print this help
        """
        instance_name = arguments['<instance>']

        inst = MechInstance(instance_name)

        if inst.created:
            vmrun = VMrun(inst.vmx, inst.user, inst.password)
            print(vmrun.list_processes_in_guest())
        else:
            print("VM {} not created.".format(instance_name))

    # alias "mech process_status" to "mech ps"
    process_status = ps

    def status(self, arguments):
        """
        Outputs status of the instances.

        Usage: mech status [options] [<instance>]

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

            if inst.created:
                vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)

                lookup = inst.enable_ip_lookup
                ip_address = vmrun.get_guest_ip_address(wait=False, quiet=True, lookup=lookup)
                state = vmrun.check_tools_state(quiet=True)

                print("Current machine state:" + os.linesep)
                if ip_address is None:
                    ip_address = "poweroff"
                elif not ip_address:
                    ip_address = "unknown"
                print("%s\t%s\t%s\t(VMware Tools %s)" % (inst.name, inst.box, ip_address, state))

                if ip_address == "poweroff":
                    print(os.linesep + "The VM is powered off. To restart the VM, "
                          "simply run `mech up {}`".format(instance))
                elif ip_address == "unknown":
                    print(os.linesep + "The VM is on. but it has no IP to connect to,"
                          "VMware Tools must be installed")
                elif state in ("installed", "running"):
                    print(os.linesep + "The VM is ready. Connect to it "
                          "using `mech ssh {}`".format(instance))
            else:
                print("The VM ({}) has not been created.".format(instance))

    def destroy(self, arguments):
        """
        Stops and deletes all traces of the instances.

        Usage: mech destroy [options] [<instance>]

        Options:
            -f, --force                      Destroy without confirmation.
            -h, --help                       Print this help
        """
        force = arguments['--force']

        instance_name = arguments['<instance>']

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)

            if os.path.exists(inst.path):
                if force or utils.confirm("Are you sure you want to delete {} "
                                          "at {}".format(inst.name, inst.path), default='n'):
                    print(colored.green("Deleting ({})...".format(instance)))
                    vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)
                    vmrun.stop(mode='hard', quiet=True)
                    vmrun.delete_vm()
                    if os.path.exists(inst.path):
                        shutil.rmtree(inst.path)
                    else:
                        LOGGER.debug("%s was not found.", inst.path)
                    print("Deleted")
                else:
                    print(colored.red("Deletion aborted"))
            else:
                print(colored.red("The box ({}) hasn't been initialized.".format(instance)))

    def down(self, arguments):
        """
        Stops the instances.

        Usage: mech down [options] [<instance>]

        Options:
                --force                      Force a hard stop
            -h, --help                       Print this help
        """
        force = arguments['--force']

        instance_name = arguments['<instance>']

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)

            if inst.created:
                vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)
                if not force and vmrun.installed_tools():
                    stopped = vmrun.stop()
                else:
                    stopped = vmrun.stop(mode='hard')
                if stopped is None:
                    print(colored.red("Not stopped", vmrun))
                else:
                    print(colored.green("Stopped", vmrun))
            else:
                print(colored.red("VM ({}) not created.".format(instance)))

    # alias 'mech stop' and 'mech halt' to 'mech down'
    stop = down
    halt = down

    def pause(self, arguments):
        """
        Pauses the instances.

        Usage: mech pause [options] [<instance>]

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

            if inst.created:
                vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)
                if vmrun.pause() is None:
                    print(colored.red("Not paused", vmrun))
                else:
                    print(colored.yellow("Paused", vmrun))
            else:
                print(colored.red("VM ({}) not created.".format(instance)))

    def resume(self, arguments):
        """
        Resume a paused/suspended instances.

        Usage: mech resume [options] [<instance>]

        Options:
            --disable-shared-folders         Do not share folders with VM
            -h, --help                       Print this help
        """
        instance_name = arguments['<instance>']
        disable_shared_folders = arguments['--disable-shared-folders']

        LOGGER.debug('instance_name:%s '
                     'disable_shared_folders:%s', instance_name, disable_shared_folders)

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)
            LOGGER.debug('instance:%s inst.vmx:%s', instance, inst.vmx)

            # if we have started this instance before, try to unpause
            if inst.created:

                vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)

                if vmrun.unpause(quiet=True) is not None:
                    print(colored.blue("Getting IP address..."))
                    lookup = inst.enable_ip_lookup
                    ip_address = vmrun.get_guest_ip_address(lookup=lookup)
                    if not disable_shared_folders:
                        print(colored.blue("Sharing current folder..."))
                        vmrun.enable_shared_folders(quiet=False)
                        vmrun.add_shared_folder('mech', utils.main_dir(), quiet=True)
                    else:
                        print(colored.blue("Disabling shared folders..."))
                        vmrun.disable_shared_folders(quiet=False)
                    if ip_address:
                        print(colored.green("VM resumed on {}".format(ip_address)))
                    else:
                        print(colored.green("VM resumed on an unknown IP address"))

                else:
                    # Otherwise try starting
                    vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)
                    started = vmrun.start()
                    if started is None:
                        print(colored.red("VM not started"))
                    else:
                        print(colored.blue("Getting IP address..."))
                        lookup = inst.enable_ip_lookup
                        ip_address = vmrun.get_guest_ip_address(lookup=lookup)
                        if not disable_shared_folders:
                            print(colored.blue("Sharing current folder..."))
                            vmrun.enable_shared_folders(quiet=False)
                            vmrun.add_shared_folder('mech', utils.main_dir(), quiet=True)
                        if ip_address:
                            if started:
                                print(colored.green("VM ({}) started on "
                                                    "{}".format(instance, ip_address)))
                            else:
                                print(colored.yellow("VM ({}) already was started "
                                                     "on {}".format(instance, ip_address)))
                        else:
                            if started:
                                print(colored.green("VM ({}) started on an unknown "
                                                    "IP address".format(instance)))
                            else:
                                print(colored.yellow("VM ({}) already was started on an "
                                                     "unknown IP address".format(instance)))
            else:
                print(colored.red("Need to start VM first"))

    def suspend(self, arguments):
        """
        Suspends instances.

        Usage: mech suspend [options] [<instance>]

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
            vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)
            if vmrun.suspend() is None:
                print(colored.red("Not suspended", vmrun))
            else:
                print(colored.green("Suspended", vmrun))

    def ssh_config(self, arguments):
        """
        Output OpenSSH valid configuration to connect to the machine.

        Usage: mech ssh-config [options] [<instance>]

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
            if inst.created:
                print(utils.config_ssh_string(inst.config_ssh()))
            else:
                print(colored.red("VM ({}) is not created.".format(instance)))

    def ssh(self, arguments):  # pylint: disable=no-self-use
        """
        Connects to machine via SSH.

        Usage: mech ssh [options] <instance> [-- <extra_ssh_args>...]

        Options:
            -c, --command COMMAND            Execute an SSH command directly
            -p, --plain                      Plain mode, leaves authentication up to user
            -h, --help                       Print this help
        """
        plain = arguments['--plain']
        extra = arguments['<extra_ssh_args>']
        command = arguments['--command']

        instance = arguments['<instance>']

        inst = MechInstance(instance)

        config_ssh = inst.config_ssh()
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            temp_file.write(utils.config_ssh_string(config_ssh).encode('utf-8'))
            temp_file.close()

            cmds = ['ssh']
            if not plain:
                cmds.extend(('-F', temp_file.name))
            if extra:
                cmds.extend(extra)
            if not plain:
                cmds.append(config_ssh['Host'])
            if command:
                cmds.extend(('--', command))

            LOGGER.debug(
                " ".join(
                    "'{}'".format(
                        c.replace(
                            "'",
                            "\\'")) if ' ' in c else c for c in cmds))
            return subprocess.call(cmds)
        finally:
            os.unlink(temp_file.name)

    def scp(self, arguments):  # pylint: disable=no-self-use
        """
        Copies files to and from the machine via SCP.

        Usage: mech scp [options] <src> <dst> [-- <extra_ssh_args>...]

        Options:
            -h, --help                       Print this help
        """
        extra = arguments['<extra_ssh_args>']
        src = arguments['<src>']
        dst = arguments['<dst>']

        dst_instance, dst_is_host, dst = dst.partition(':')
        src_instance, src_is_host, src = src.partition(':')

        if dst_is_host and src_is_host:
            print(colored.red("Both src and host are host destinations"))
            sys.exit(1)
        if dst_is_host:
            instance = dst_instance
        else:
            dst = dst_instance
        if src_is_host:
            instance = src_instance
        else:
            src = src_instance

        inst = MechInstance(instance)

        config_ssh = inst.config_ssh()
        temp_file = tempfile.NamedTemporaryFile(delete=False)

        try:
            temp_file.write(utils.config_ssh_string(config_ssh).encode())
            temp_file.close()

            cmds = ['scp']
            cmds.extend(('-F', temp_file.name))
            if extra:
                cmds.extend(extra)

            host = config_ssh['Host']
            dst = '{}:{}'.format(host, dst) if dst_is_host else dst
            src = '{}:{}'.format(host, src) if src_is_host else src
            cmds.extend((src, dst))

            LOGGER.debug(
                " ".join(
                    "'{}'".format(
                        c.replace(
                            "'",
                            "\\'")) if ' ' in c else c for c in cmds))
            return subprocess.call(cmds)
        finally:
            os.unlink(temp_file.name)

    def ip(self, arguments):  # pylint: disable=invalid-name,no-self-use
        """
        Outputs ip of the Mech machine.

        Usage: mech ip [options] <instance>

        Options:
            -h, --help                       Print this help
        """
        instance = arguments['<instance>']

        inst = MechInstance(instance)

        if inst.created:
            vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)
            lookup = inst.enable_ip_lookup
            ip_address = vmrun.get_guest_ip_address(lookup=lookup)
            if ip_address:
                print(colored.green(ip_address))
            else:
                print(colored.red("Unknown IP address"))
        else:
            print(colored.yellow("VM not created"))

    # alias 'mech ip_address' to 'mech ip'
    ip_address = ip

    def provision(self, arguments):
        """
        Provisions the Mech machine.

        Usage: mech provision [options] [<instance>]

        Options:
            -s, --show-only                  Show the provisioning info (do not run)
            -h, --help                       Print this help
        """
        show = arguments['--show-only']
        instance_name = arguments['<instance>']

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            inst = MechInstance(instance)
            utils.provision(instance, inst.vmx, inst.user, inst.password, inst.provision, show)

    def reload(self, arguments):
        """
        Restarts Mech machine, loads new Mechfile configuration.

        Usage: mech reload [options] [<instance>]

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

            vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)

            print(colored.blue("Reloading machine..."))
            started = vmrun.reset()
            if started is None:
                print(colored.red("VM not restarted"))
            else:
                print(colored.blue("Getting IP address..."))
                lookup = inst.enable_ip_lookup
                ip_address = vmrun.get_guest_ip_address(lookup=lookup)
                if ip_address:
                    if started:
                        print(colored.green("VM ({}) started "
                                            "on {}".format(instance, ip_address)))
                    else:
                        print(colored.yellow("VM ({}) already was started on "
                                             "{}".format(instance, ip_address)))
                else:
                    if started:
                        print(colored.green("VM ({}) started on an unknown IP "
                                            "address".format(instance)))
                    else:
                        print(colored.yellow("VM ({}) already was started "
                                             "on an unknown IP address".format(instance)))

    def port(self, arguments):
        """
        Displays information about guest port mappings.

        Usage: mech port [options] [<instance>]

        Options:
                --guest PORT                 Output the host port that maps to the given guest port
                --machine-readable           Display machine-readable output
            -h, --help                       Print this help
        """
        instance_name = arguments['<instance>']

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        # FUTURE: implement port forwarding?
        for instance in instances:
            inst = MechInstance(instance)

            print('Instance ({}):'. format(instance))
            nat_found = False
            vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)
            for line in vmrun.list_host_networks().split('\n'):
                network = line.split()
                if len(network) > 2 and network[2] == 'nat':
                    print(vmrun.list_port_forwardings(network[1]))
                    nat_found = True
            if not nat_found:
                print(colored.red("Cannot find a nat network"), file=sys.stderr)

    def list(self, arguments):
        """
        Lists all available boxes from Mechfile.

        Usage: mech list [options]

        Options:
            -d, --detail                     Print detailed info
            -h, --help                       Print this help
        """

        detail = arguments['--detail']

        self.activate_mechfile()

        if detail:
            print('Instance Details')
            print()
        else:
            print("{}\t{}\t{}\t{}".format(
                'NAME'.rjust(20),
                'ADDRESS'.rjust(15),
                'BOX'.rjust(35),
                'VERSION'.rjust(12)
            ))

        for name in self.mechfile:
            inst = MechInstance(name, self.mechfile)
            if inst.created:
                vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)
                lookup = inst.enable_ip_lookup
                ip_address = vmrun.get_guest_ip_address(wait=False, quiet=True, lookup=lookup)
                if ip_address is None:
                    ip_address = colored.yellow("poweroff")
                elif not ip_address:
                    ip_address = colored.green("running")
                else:
                    ip_address = colored.green(ip_address)
            else:
                ip_address = "notcreated"

            if detail:
                print(inst)
                print()
            else:
                print("{}\t{}\t{}\t{}".format(
                    colored.green(name.rjust(20)),
                    ip_address.rjust(15),
                    inst.box.rjust(35),
                    inst.box_version.rjust(12)
                ))

    # allow 'mech ls' as alias to 'mech list'
    ls = list
