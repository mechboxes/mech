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

from __future__ import print_function, absolute_import

import os
import re
import sys
import time
import fnmatch
import logging
import tempfile
import textwrap
import shutil
import subprocess

from clint.textui import colored, puts_err

from . import utils
from .vmrun import VMrun
from .command import Command

logger = logging.getLogger(__name__)

DEFAULT_HOST = 'mech'
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

MECH_DIR = os.path.expanduser(os.getcwd() + '/.mech')


class MechCommand(Command):
    mechfile = None
    active_name = None
    created = False
    box = None
    box_version = None
    url = None
    vmx = None
    user = None
    password = None
    enable_ip_lookup = False

    def activate_mechfile(self):
        """Load the Mechfile."""
        self.mechfile = utils.load_mechfile()

    def instances(self):
        """Returns a list of the instances from the Mechfile."""
        if not self.mechfile:
            self.activate_mechfile()
        return list(self.mechfile)

    @staticmethod
    def instance_path(name):
        """Return the path for an instance."""
        return os.path.join(MECH_DIR, name)

    def deactivate(self):
        """Make it so we do have have an active instance selected."""
        self.active_name = None
        self.created = False
        self.box = None
        self.box_version = None
        self.url = None
        self.vmx = None
        self.user = None
        self.password = None
        self.enable_ip_lookup = False
        os.chdir(MECH_DIR)

    def activate(self, name):
        """Sets the active instance name and changes to the
           directory for that instance."""
        if not self.mechfile:
            self.activate_mechfile()
        if name == "":
            raise AttributeError("Must activate with name.")
        if self.mechfile.get(name, None):
            self.active_name = name
        else:
            puts_err(colored.red("Instance ({}) was not found in the Mechfile".format(name)))
            sys.exit(1)
        self.box = self.mechfile[name].get('box', None)
        self.box_version = self.mechfile[name].get('box_version', None)
        self.url = self.mechfile[name].get('url', None)
        self.user = DEFAULT_USER
        self.password = DEFAULT_PASSWORD
        path = MechCommand.instance_path(name)
        vmx = utils.locate(path, '*.vmx')
        # Note: If vm has not been started vmx will be None
        if vmx:
            self.vmx = vmx
            self.created = True
        else:
            self.vmx = None
            self.created = False
        if os.path.exists(path):
            # change to the path of the instance
            os.chdir(path)

    def vmx(self):
        """Get the fully qualified path to the vmx file."""
        return self.vmx

    def box(self):
        """Get the box (ex: 'bento/ubuntu-18.04')."""
        return self.box

    def box_version(self):
        """Get the box_version (ex: '2020-01-16')."""
        return self.box_version

    def user(self):
        """Get the username (ex: 'vagrant')."""
        return self.user

    def password(self):
        """Get the password (ex: 'temp123')."""
        return self.password

    def enable_ip_lookup(self):
        """Enable ip lookup (defaults to False)."""
        return self.enable_ip_lookup

    @property
    def config(self):
        return self.get('config', {}).get('ssh', {})

    @property
    def config_ssh(self):
        vmrun = VMrun(self.vmx, user=self.user, password=self.password)
        lookup = self.enable_ip_lookup
        ip = vmrun.getGuestIPAddress(wait=False, lookup=lookup) if vmrun.installedTools() else None
        if not ip:
            puts_err(colored.red(textwrap.fill(
                "This Mech machine is reporting that it is not yet ready for SSH. "
                "Make sure your machine is created and running and try again. "
                "Additionally, check the output of `mech status` to verify "
                "that the machine is in the state that you expect."
            )))
            sys.exit(1)

        insecure_private_key = os.path.abspath(os.path.join(MECH_DIR, "insecure_private_key"))
        if not os.path.exists(insecure_private_key):
            with open(insecure_private_key, 'w') as f:
                f.write(INSECURE_PRIVATE_KEY)
            os.chmod(insecure_private_key, 0o400)
        config = {
            "Host": self.active_name,
            "User": self.user,
            "Port": "22",
            "UserKnownHostsFile": "/dev/null",
            "StrictHostKeyChecking": "no",
            "PasswordAuthentication": "no",
            "IdentityFile": insecure_private_key,
            "IdentitiesOnly": "yes",
            "LogLevel": "FATAL",
        }
        for k, v in self.config.items():
            k = re.sub(r'[ _]+', r' ', k)
            k = re.sub(r'(?<=[^_])([A-Z])', r' \1', k).lower()
            k = re.sub(r'^( *)(.*?)( *)$', r'\2', k)

            def callback(pat):
                return pat.group(1).upper()

            k = re.sub(r' (\w)', callback, k)
            if k[0].islower():
                k = k[0].upper() + k[1:]
            config[k] = v
        config.update({
            "HostName": ip,
        })
        return config


class MechBox(MechCommand):
    """
    Usage: mech box <subcommand> [<args>...]

    Available subcommands:
        add               add a box to the catalog of available boxes
        list              list available boxes in the catalog
        outdated          checks for outdated boxes
        remove            removes a box that matches the given name
        update

    For help on any individual subcommand run `mech box <subcommand> -h`
    """

    def add(self, arguments):
        """
        Add a box to the catalog of available boxes.

        Usage: mech box add [options] [<name>] [<location>]

        Notes:
            The box descriptor can be the name of a box on HashiCorp's Vagrant Cloud,
            or a URL, a local .box or .tar file, or a local .json file containing
            the catalog metadata.

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
        url = arguments['<location>']
        if url:
            name = arguments['<name>']
        else:
            url = arguments['<name>']
            name = None
        version = arguments['--box-version']
        force = arguments['--force']
        requests_kwargs = utils.get_requests_kwargs(arguments)
        utils.add_box(url, name=name, version=version, force=force, requests_kwargs=requests_kwargs)

    def list(self, arguments):
        """
        List all available boxes in the catalog.

        Usage: mech box list [options]

        Options:
            -i, --box-info                   Displays additional information about the boxes
            -h, --help                       Print this help
        """

        print("{}\t{}".format(
            'BOX'.rjust(35),
            'VERSION'.rjust(12),
        ))
        path = os.path.abspath(os.path.join(MECH_DIR, 'boxes'))
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, '*.box'):
                directory = os.path.dirname(os.path.join(root, filename))[len(path) + 1:]
                account, box, version = (directory.split('/', 2) + ['', ''])[:3]
                print("{}\t{}".format(
                    "{}/{}".format(account, box).rjust(35),
                    version.rjust(12),
                ))
    ls = list

    def outdated(self, arguments):
        """
        Checks if there is a new version available for the box.

        Usage: mech box outdated [options]

        Options:
                --global                     Check all boxes installed
                --insecure                   Do not validate SSL certificates
                --cacert FILE                CA certificate for SSL download
                --capath DIR                 CA certificate directory for SSL download
                --cert FILE                  A client SSL cert, if needed
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))

    def remove(self, arguments):
        """
        Remove a box from mech that matches the given name.

        Usage: mech box remove [options] <name>

        Options:
            -f, --force                      Remove without confirmation.
                --box-version VERSION        The specific version of the box to remove
                --all                        Remove all available versions of the box
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))

    def update(self, arguments):
        """
        Update the box that is in use in the current mech environment.

        Usage: mech box update [options] [<name>]

        Notes:
            Only if there any updates available. This does not destroy/recreate
            the machine, so you'll have to do that to see changes.

        Options:
            -f, --force                      Overwrite an existing box if it exists
                --insecure                   Do not validate SSL certificates
                --cacert FILE                CA certificate for SSL download
                --capath DIR                 CA certificate directory for SSL download
                --cert FILE                  A client SSL cert, if needed
            -h, --help                       Print this help
        """
        puts_err(colored.red("Not implemented!"))


class MechSnapshot(MechCommand):
    """
    Usage: mech snapshot <subcommand> [<args>...]

    Available subcommands:
        delete            delete a snapshot taken previously with snapshot save
        list              list all snapshots taken for a machine
        save              take a snapshot of the current state of the machine

    For help on any individual subcommand run `mech snapshot <subcommand> -h`
    """

    def delete(self, arguments):
        """
        Delete a snapshot taken previously with snapshot save.

        Usage: mech snapshot delete [options] <name> [<instance>]

        Options:
            -h, --help                       Print this help
        """
        name = arguments['<name>']

        instance_name = arguments['<instance>']

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            self.activate(instance)

            vmrun = VMrun(self.vmx, user=self.user, password=self.password)
            if vmrun.deleteSnapshot(name) is None:
                puts_err(colored.red("Cannot delete name"))
            else:
                puts_err(colored.green("Snapshot {} deleted".format(name)))

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
            self.activate(instance)
            vmrun = VMrun(self.vmx, user=self.user, password=self.password)
            print(vmrun.listSnapshots())

    def save(self, arguments):
        """
        Take a snapshot of the current state of the machine.

        Usage: mech snapshot save [options] <name> [<instance>]

        Notes:
            Take a snapshot of the current state of the machine. The snapshot
            can be restored via `mech snapshot restore` at any point in the
            future to get back to this exact machine state.

            Snapshots are useful for experimenting in a machine and being able
            to rollback quickly.

        Options:
            -f  --force                      Replace snapshot without confirmation
            -h, --help                       Print this help
        """
        name = arguments['<name>']

        instance_name = arguments['<instance>']

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            self.activate(instance)
            vmrun = VMrun(self.vmx, user=self.user, password=self.password)
            if vmrun.snapshot(name) is None:
                puts_err(colored.red("Cannot take snapshot"))
            else:
                puts_err(colored.green("Snapshot {} taken".format(name)))


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
        destroy           stops and deletes all traces of the Mech machine
        (up|start)        starts and provisions the Mech environment
        (down|stop|halt)  stops the Mech machine
        suspend           suspends the machine
        pause             pauses the Mech machine
        ssh               connects to machine via SSH
        ssh-config        outputs OpenSSH valid configuration to connect to the machine
        scp               copies files to and from the machine via SCP
        ip                outputs ip of the Mech machine
        box               manages boxes: installation, removal, etc.
        global-status     outputs status Mech environments for this user
        status            outputs status of the Mech machine
        ps                list running processes in Guest OS
        provision         provisions the Mech machine
        reload            restarts Mech machine, loads new Mechfile configuration
        resume            resume a paused/suspended Mech machine
        snapshot          manages snapshots: saving, restoring, etc.
        port              displays information about guest port mappings
        push              deploys code in this environment to a configured destination

    For help on any individual command run `mech <command> -h`

    Example:

    Initializing and using a machine from HashiCorp's Vagrant Cloud:

        mech init bento/ubuntu-14.04
        mech up
        mech ssh
    """

    subcommand_name = '<command>'

    def __init__(self, arguments):
        super(Mech, self).__init__(arguments)

        logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        if arguments['--debug']:
            logger.setLevel(logging.DEBUG)

    box = MechBox
    snapshot = MechSnapshot

    def init(self, arguments):
        """
        Initializes a new mech environment by creating a Mechfile.

        Usage: mech init [options] <box>

        Example box: bento/ubuntu-18.04

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
        box = arguments['<box>']

        if not name or name == "":
            name = "first"

        force = arguments['--force']
        requests_kwargs = utils.get_requests_kwargs(arguments)

        if os.path.exists('Mechfile') and not force:
            puts_err(colored.red(textwrap.fill(
                "`Mechfile` already exists in this directory. Remove it "
                "before running `mech init`."
            )))
            return

        puts_err(colored.green("Initializing mech"))
        if utils.init_mechfile(
                box,
                name=name,
                box_version=box_version,
                requests_kwargs=requests_kwargs):
            puts_err(colored.green(textwrap.fill(
                "A `Mechfile` has been initialized and placed in this directory. "
                "You are now ready to `mech up` your first virtual environment!"
            )))
        else:
            puts_err(colored.red("Couldn't initialize mech"))

    def up(self, arguments):
        """
        Starts and provisions the mech environment.

        Usage: mech up [options] [<instance>]

        Note: If no instance is specified, all instances will be started.

        Options:
                --gui                        Start GUI
                --disable-shared-folder      Do not share folder with VM
                --provision                  Enable provisioning
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
        disable_shared_folder = not arguments['--disable-shared-folder']
        save = not arguments['--no-cache']
        requests_kwargs = utils.get_requests_kwargs(arguments)

        numvcpus = arguments['--numvcpus']
        memsize = arguments['--memsize']

        instance_name = arguments['<instance>']

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            self.activate(instance)
            instance_path = MechCommand.instance_path(instance)

            vmx = utils.init_box(
                instance,
                box=self.box,
                box_version=self.box_version,
                instance_path=instance_path,
                requests_kwargs=requests_kwargs,
                save=save,
                numvcpus=numvcpus,
                memsize=memsize)
            if vmx:
                self.vmx = vmx
                self.created = True

            vmrun = VMrun(vmx, user=self.user, password=self.password)
            puts_err(colored.blue("Bringing machine up..."))
            started = vmrun.start(gui=gui)
            if started is None:
                puts_err(colored.red("VM not started"))
            else:
                time.sleep(3)
                puts_err(colored.blue("Getting IP address..."))
                lookup = self.enable_ip_lookup
                ip = vmrun.getGuestIPAddress(lookup=lookup)
                puts_err(colored.blue("Sharing current folder..."))
                if not disable_shared_folder:
                    vmrun.enableSharedFolders()
                    vmrun.addSharedFolder('mech', os.getcwd(), quiet=True)
                if ip:
                    if started:
                        puts_err(colored.green("VM started on {}".format(ip)))
                    else:
                        puts_err(colored.yellow("VM was already started on {}".format(ip)))
                else:
                    if started:
                        puts_err(colored.green("VM started on an unknown IP address"))
                    else:
                        puts_err(colored.yellow("VM was already started on an unknown IP address"))

    # allows "mech start" to alias to "mech up"
    start = up

    def global_status(self, arguments):
        """
        Outputs mech environments status for this user.

        Usage: mech global-status [options]

        Options:
                --prune                      Prune invalid entries
            -h, --help                       Print this help
        """
        vmrun = VMrun()
        print(vmrun.list())

    def ps(self, arguments):
        """
        List running processes in Guest OS.

        Usage: mech ps [options] [<instance>]

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
            self.activate(instance)
            vmrun = VMrun(self.vmx, self.user, self.password)
            print(vmrun.listProcessesInGuest())

    def status(self, arguments):
        """
        Outputs status of the Mech machine.

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
            self.activate(instance)

            vmrun = VMrun(self.vmx, user=self.user, password=self.password)

            lookup = self.enable_ip_lookup
            ip = vmrun.getGuestIPAddress(wait=False, quiet=True, lookup=lookup)
            state = vmrun.checkToolsState(quiet=True)

            print("Current machine state:" + os.linesep)
            if ip is None:
                ip = "poweroff"
            elif not ip:
                ip = "unknown"
            print("%s\t%s\t%s\t(VMware Tools %s)" % (self.active_name, self.box, ip, state))

            if ip == "poweroff":
                print(os.linesep + "The VM is powered off. To restart the VM, "
                      "simply run `mech up {}`".format(instance))
            elif ip == "unknown":
                print(os.linesep + "The VM is on. but it has no IP to connect to,"
                      "VMware Tools must be installed")
            elif state in ("installed", "running"):
                print(os.linesep + "The VM is ready. Connect to it "
                      "using `mech ssh {}`".format(instance))

    def destroy(self, arguments):
        """
        Stops and deletes all traces of the Mech machine.

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
            self.activate(instance)

            if self.active_name:
                instance_path = MechCommand.instance_path(instance)

            if os.path.exists(instance_path):
                if force or utils.confirm(
                    "Are you sure you want to delete {} at {}".format(
                        self.active_name, instance_path), default='n'):
                    puts_err(colored.green("Deleting..."))
                    vmrun = VMrun(self.vmx, user=self.user, password=self.password)
                    vmrun.stop(mode='hard', quiet=True)
                    time.sleep(3)
                    vmrun.deleteVM()

                    # change out of this directory
                    self.deactivate()

                    if os.path.exists(instance_path):
                        shutil.rmtree(instance_path)
                    else:
                        logger.debug("{} was not found.".format(instance_path))
                else:
                    puts_err(colored.red("Deletion aborted"))
            else:
                puts_err(colored.red("The box hasn't been initialized."))

    def down(self, arguments):
        """
        Stops the Mech machine.

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
            self.activate(instance)

            vmrun = VMrun(self.vmx, user=self.user, password=self.password)
            if not force and vmrun.installedTools():
                stopped = vmrun.stop()
            else:
                stopped = vmrun.stop(mode='hard')
            if stopped is None:
                puts_err(colored.red("Not stopped", vmrun))
            else:
                puts_err(colored.green("Stopped", vmrun))

    # alias 'mech stop' and 'mech halt' to 'mech down'
    stop = down
    halt = down

    def pause(self, arguments):
        """
        Pauses the Mech machine.

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
            self.activate(instance)
            vmrun = VMrun(self.vmx, user=self.user, password=self.password)
            if vmrun.pause() is None:
                puts_err(colored.red("Not paused", vmrun))
            else:
                puts_err(colored.yellow("Paused", vmrun))

    def resume(self, arguments):
        """
        Resume a paused/suspended Mech machine.

        Usage: mech resume [options] [<instance>]

        Options:
                --provision                  Enable provisioning
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
            self.activate(instance)

            vmrun = VMrun(self.vmx, user=self.user, password=self.password)

            # Try to unpause
            if vmrun.unpause(quiet=True) is not None:
                time.sleep(1)
                puts_err(colored.blue("Getting IP address..."))
                lookup = self.enable_ip_lookup
                ip = vmrun.getGuestIPAddress(lookup=lookup)
                if ip:
                    puts_err(colored.green("VM resumed on {}".format(ip)))
                else:
                    puts_err(colored.green("VM resumed on an unknown IP address"))

            # Otherwise try starting
            else:
                started = vmrun.start()
                if started is None:
                    puts_err(colored.red("VM not started"))
                else:
                    time.sleep(3)
                    puts_err(colored.blue("Getting IP address..."))
                    lookup = self.enable_ip_lookup
                    ip = vmrun.getGuestIPAddress(lookup=lookup)
                    puts_err(colored.blue("Sharing current folder..."))
                    vmrun.enableSharedFolders()
                    vmrun.addSharedFolder('mech', os.getcwd(), quiet=True)
                    if ip:
                        if started:
                            puts_err(colored.green("VM started on {}".format(ip)))
                        else:
                            puts_err(colored.yellow("VM already was started on {}".format(ip)))
                    else:
                        if started:
                            puts_err(colored.green("VM started on an unknown IP address"))
                        else:
                            puts_err(colored.yellow("VM already was started "
                                     "on an unknown IP address"))

    def suspend(self, arguments):
        """
        Suspends the machine.

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
            self.activate(instance)
            vmrun = VMrun(self.vmx, user=self.user, password=self.password)
            if vmrun.suspend() is None:
                puts_err(colored.red("Not suspended", vmrun))
            else:
                puts_err(colored.green("Suspended", vmrun))

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
            self.activate(instance)
            print(utils.config_ssh_string(self.config_ssh))

    def ssh(self, arguments):
        """
        Connects to machine via SSH.

        Usage: mech ssh [options] [<instance>] [-- <extra_ssh_args>...]

        Options:
            -c, --command COMMAND            Execute an SSH command directly
            -p, --plain                      Plain mode, leaves authentication up to user
            -h, --help                       Print this help
        """
        plain = arguments['--plain']
        extra = arguments['<extra_ssh_args>']
        command = arguments['--command']

        instance_name = arguments['<instance>']

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # multiple instances
            instances = self.instances()

        for instance in instances:
            self.activate(instance)

            config_ssh = self.config_ssh
            fp = tempfile.NamedTemporaryFile(delete=False)
            try:
                fp.write(utils.config_ssh_string(config_ssh).encode('utf-8'))
                fp.close()

                cmds = ['ssh']
                if not plain:
                    cmds.extend(('-F', fp.name))
                if extra:
                    cmds.extend(extra)
                if not plain:
                    cmds.append(config_ssh['Host'])
                if command:
                    cmds.extend(('--', command))

                logger.debug(
                    " ".join(
                        "'{}'".format(
                            c.replace(
                                "'",
                                "\\'")) if ' ' in c else c for c in cmds))
                return subprocess.call(cmds)
            finally:
                os.unlink(fp.name)

    def scp(self, arguments):
        """
        Copies files to and from the machine via SCP.

        Usage: mech scp [options] <src> <dst> [-- <extra scp args>...]

        Options:
            -h, --help                       Print this help
        """
        extra = arguments['<extra scp args>']
        src = arguments['<src>']
        dst = arguments['<dst>']

        dst_instance, dst_is_host, dst = dst.partition(':')
        src_instance, src_is_host, src = src.partition(':')

        # TODO: review this
        if dst_is_host and src_is_host:
            puts_err(colored.red("Both src and host are host destinations"))
            sys.exit(1)
        if dst_is_host:
            instance_name = dst_instance
        else:
            dst = dst_instance
        if src_is_host:
            instance_name = src_instance
        else:
            src = src_instance

        self.instance_name = self.activate(instance_name)

        config_ssh = self.config_ssh
        fp = tempfile.NamedTemporaryFile(delete=False)
        try:
            fp.write(utils.config_ssh_string(config_ssh))
            fp.close()

            cmds = ['scp']
            cmds.extend(('-F', fp.name))
            if extra:
                cmds.extend(extra)

            host = config_ssh['Host']
            dst = '{}:{}'.format(host, dst) if dst_is_host else dst
            src = '{}:{}'.format(host, src) if src_is_host else src
            cmds.extend((src, dst))

            logger.debug(
                " ".join(
                    "'{}'".format(
                        c.replace(
                            "'",
                            "\\'")) if ' ' in c else c for c in cmds))
            return subprocess.call(cmds)
        finally:
            os.unlink(fp.name)

    def ip(self, arguments):
        """
        Outputs ip of the Mech machine.

        Usage: mech ip [options] [<instance>]

        Options:
            -h, --help                       Print this help
        """
        instance_name = arguments['<instance>']

        if instance_name:
            # single instance
            instances = [instance_name]
        else:
            # TODO: Does it make sense to have multiple?
            # multiple instances
            instances = self.instances()

        for instance in instances:
            self.activate(instance)

            if self.created:
                vmrun = VMrun(self.vmx, user=self.user, password=self.password)
                lookup = self.enable_ip_lookup
                ip = vmrun.getGuestIPAddress(lookup=lookup)
                if ip:
                    puts_err(colored.green(ip))
                else:
                    puts_err(colored.red("Unknown IP address"))
            else:
                puts_err(colored.yellow("VM not created"))

    def provision(self, arguments):
        """
        Provisions the Mech machine.

        Usage: mech provision [options] [<instance>]

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
            self.activate(instance)

            vmrun = VMrun(self.vmx, self.user, self.password)

            if not vmrun.installedTools():
                puts_err(colored.red("Tools not installed"))
                return

            provisioned = 0
            for i, provision in enumerate(self.get('provision', [])):

                # TODO: re-review this
                if provision.get('type') == 'file':
                    source = provision.get('source')
                    destination = provision.get('destination')
                    if utils.provision_file(vmrun, source, destination) is None:
                        puts_err(colored.red("Not Provisioned"))
                        return
                    provisioned += 1

                elif provision.get('type') == 'shell':
                    inline = provision.get('inline')
                    path = provision.get('path')
                    args = provision.get('args')
                    if not isinstance(args, list):
                        args = [args]
                    if utils.provision_shell(vmrun, inline, path, args) is None:
                        puts_err(colored.red("Not Provisioned"))
                        return
                    provisioned += 1

                else:
                    puts_err(colored.red("Not Provisioned ({}".format(i)))
                    return
            else:
                puts_err(colored.green("Provisioned {} entries".format(provisioned)))
                return

            puts_err(colored.red("Not Provisioned ({}".format(i)))

    def reload(self, arguments):
        """
        Restarts Mech machine, loads new Mechfile configuration.

        Usage: mech reload [options] [<instance>]

        Options:
                --provision                  Enable provisioning
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
            self.activate(instance)

            vmrun = VMrun(self.vmx, user=self.user, password=self.password)

            puts_err(colored.blue("Reloading machine..."))
            started = vmrun.reset()
            if started is None:
                puts_err(colored.red("VM not restarted"))
            else:
                time.sleep(3)
                puts_err(colored.blue("Getting IP address..."))
                lookup = self.enable_ip_lookup
                ip = vmrun.getGuestIPAddress(lookup=lookup)
                if ip:
                    if started:
                        puts_err(colored.green("VM started on {}".format(ip)))
                    else:
                        puts_err(colored.yellow("VM already was started on {}".format(ip)))
                else:
                    if started:
                        puts_err(colored.green("VM started on an unknown IP address"))
                    else:
                        puts_err(colored.yellow("VM already was started on an unknown IP address"))

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

        # TODO: implement port forwarding?
        for instance in instances:
            self.activate(instance)

            vmrun = VMrun(self.vmx, user=self.user, password=self.password)
            for network in vmrun.listHostNetworks().split('\n'):
                network = network.split()
                if len(network) > 2 and network[2] == 'nat':
                    print(vmrun.listPortForwardings(network[1]))
                    break
            else:
                puts_err(colored.red("Cannot find a nat network"))

    def list(self, arguments):
        """
        Lists all available boxes.

        Usage: mech list [options]

        Options:
            -h, --help                       Print this help
        """

        self.activate_mechfile()

        print("{}\t{}\t{}\t{}".format(
            'NAME'.rjust(20),
            'ADDRESS'.rjust(15),
            'BOX'.rjust(35),
            'VERSION'.rjust(12)
        ))
        for name in self.mechfile:
            self.activate(name)
            if self.created:
                vmrun = VMrun(self.vmx, user=self.user, password=self.password)
                lookup = self.enable_ip_lookup
                ip = vmrun.getGuestIPAddress(wait=False, quiet=True, lookup=lookup)
                if ip is None:
                    ip = colored.yellow("poweroff")
                elif not ip:
                    ip = colored.green("running")
                else:
                    ip = colored.green(ip)
            else:
                ip = "notcreated"

            print("{}\t{}\t{}\t{}".format(
                colored.green(name.rjust(20)),
                ip.rjust(15),
                self.box.rjust(35),
                self.box_version.rjust(12)
            ))

    # allow 'mech ls' as alias to 'mech list'
    ls = list
