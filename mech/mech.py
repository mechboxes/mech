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
"""Mech class"""

from __future__ import print_function, absolute_import

import os
import sys
import logging
import textwrap
import shutil

from clint.textui import colored

from . import utils
from .vmrun import VMrun
from .mech_instance import MechInstance
from .mech_command import MechCommand
from .mech_box import MechBox
from .mech_snapshot import MechSnapshot

LOGGER = logging.getLogger(__name__)


class Mech(MechCommand):
    """
    Usage: mech [options] <command> [<args>...]

    Options:
        -v, --version                    Print the version and exit.
        -h, --help                       Print this help.
        --debug                          Show debug messages.

    Common commands:
        box               manages boxes: add, list remove, etc.
        destroy           stops and deletes all traces of the instances
        (down|stop|halt)  stops the instances
        global-status     outputs status of all virutal machines on this host
        init              initializes a new Mech environment by creating a Mechfile
        ip                outputs ip of an instance
        (list|ls)         lists all available boxes
        pause             pauses the instances
        port              displays information about guest port mappings
        provision         provisions the Mech machine
        ps                list running processes for an instance
        reload            restarts Mech machine, loads new Mechfile configuration
        resume            resume a paused/suspended Mech machine
        scp               copies files to/from the machine via SCP
        snapshot          manages snapshots: save, list, remove, etc.
        ssh               connects to an instance via SSH
        ssh-config        outputs OpenSSH valid configuration to connect to the instances
        status            outputs status of the instances
        suspend           suspends the instances
        (up|start)        starts instances (aka virtual machines)
        upgrade           upgrade the instances

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
          - The location can be a:
              + URL (ex: 'http://example.com/foo.box'),
              + box file (ex: 'file:/mnt/boxen/foo.box'),
              + json file (ex: 'file:/tmp/foo.json'), or
              + HashiCorp account/box (ex: 'bento/ubuntu-18.04').
          - A default shared folder name 'mech' will be available
            in the guest for the current directory.
          - The 'add-me' option will add the currently logged in user to the guest,
            add the same user to sudoers, and add the id_rsa.pub key to the
            authorized_hosts file for that user.
          - The 'use-me' option will use the currently logged in user for
            future interactions with the guest instead of the vagrant user.
            The first provisioning run will be done with 'vagrant' user.

        Options:
            -a, --add-me                     Add the current host user/pubkey to guest
                --box BOXNAME                Name of the box (ex: bento/ubuntu-18.04)
                --box-version VERSION        Constrain version of the added box
            -f, --force                      Overwrite existing Mechfile
            -h, --help                       Print this help
                --name INSTANCE              Name of the instance (myinst1)
            -u, --use-me                     Use the current user for mech interactions
        """
        add_me = arguments['--add-me']
        use_me = arguments['--use-me']
        name = arguments['--name']
        box_version = arguments['--box-version']
        box = arguments['--box']
        location = arguments['<location>']

        if not name or name == "":
            name = "first"

        force = arguments['--force']

        LOGGER.debug('name:%s box:%s box_version:%s location:%s', name, box, box_version, location)

        if os.path.exists('Mechfile') and not force:
            sys.exit(colored.red(textwrap.fill(
                "`Mechfile` already exists in this directory. Remove it "
                "before running `mech init`.")))

        print(colored.green("Initializing mech"))
        utils.init_mechfile(
            location=location,
            box=box,
            name=name,
            box_version=box_version,
            add_me=add_me,
            use_me=use_me)
        print(colored.green(textwrap.fill(
            "A `Mechfile` has been initialized and placed in this directory. "
            "You are now ready to `mech up` your first virtual environment!")))

    def add(self, arguments):  # pylint: disable=no-self-use
        """
        Add instance to the Mechfile.

        Usage: mech add [options] <name> <location>

        Example box: bento/ubuntu-18.04

        Notes:
        - The 'add-me' option will add the currently logged in user to the guest,
          add the same user to sudoers, and add the id_rsa.pub key to the authorized_hosts file
          for that user.

        Options:
            -a, --add-me                     Add the current host user/pubkey to guest
                --box BOXNAME                Name of the box (ex: bento/ubuntu-18.04)
                --box-version VERSION        Constrain version of the added box
            -h, --help                       Print this help
            -u, --use-me                     Use the current user for mech interactions
        """
        name = arguments['<name>']
        box_version = arguments['--box-version']
        box = arguments['--box']
        add_me = arguments['--add-me']
        use_me = arguments['--use-me']
        location = arguments['<location>']

        if not name or name == "":
            sys.exit(colored.red("Need to provide a name for the instance to add to the Mechfile."))

        LOGGER.debug('name:%s box:%s box_version:%s location:%s', name, box, box_version, location)

        print(colored.green("Adding ({}) to the Mechfile.".format(name)))

        utils.add_to_mechfile(
            location=location,
            box=box,
            name=name,
            box_version=box_version,
            add_me=add_me,
            use_me=use_me)
        print(colored.green("Added to the Mechfile."))

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
            utils.remove_mechfile_entry(name=name)
            print(colored.green("Removed from the Mechfile."))
        else:
            sys.exit(colored.red("There is no instance called ({}) in the Mechfile.".format(name)))

    # add aliases for 'mech delete'
    delete = remove
    rm = remove

    def up(self, arguments):  # pylint: disable=invalid-name
        """
        Starts and provisions the mech environment.

        Usage: mech up [options] [<instance>]

        Notes:
           - If no instance is specified, all instances will be started.
           - The options (memsize, numvcpus, and no-nat) will only be applied
             upon first run of the 'up' command.
           - The 'no-nat' option will only be applied if there is no network
             interface supplied in the box file.
           - Unless 'disable-shared-folders' is used, a default read/write
             share called "mech" will be mounted from the current directory.
             (ex: '/mnt/hgfs/mech' on guest will have the file "Mechfile".)
             To change shared folders, modify the Mechfile directly.
           - The 'remove-vagrant' option will remove the vagrant account from the
             guest VM which is what 'mech' uses to communicate with the VM.
             Be sure you can connect/admin the instance before using this option.

        Options:
                --disable-provisioning       Do not provision
                --disable-shared-folders     Do not share folders with VM
                --gui                        Start GUI
                --memsize 1024               Specify the size of memory for VM
                --no-cache                   Do not save the downloaded box
                --no-nat                     Do not use NAT network (i.e., bridged)
                --numvcpus 1                 Specify the number of vcpus for VM
            -h, --help                       Print this help
            -r, --remove-vagrant             Remove vagrant user
        """
        gui = arguments['--gui']
        disable_shared_folders = arguments['--disable-shared-folders']
        disable_provisioning = arguments['--disable-provisioning']
        save = not arguments['--no-cache']
        remove_vagrant = arguments['--remove-vagrant']

        memsize = arguments['--memsize']
        numvcpus = arguments['--numvcpus']
        no_nat = arguments['--no-nat']

        instance_name = arguments['<instance>']

        LOGGER.debug('gui:%s disable_shared_folders:%s disable_provisioning:%s '
                     'save:%s numvcpus:%s memsize:%s no_nat:%s', gui,
                     disable_shared_folders, disable_provisioning, save,
                     numvcpus, memsize, no_nat)

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

            # only run init_box on first "up"
            if not inst.created:
                inst.vmx = utils.init_box(
                    instance,
                    box=inst.box,
                    box_version=inst.box_version,
                    location=location,
                    instance_path=inst.path,
                    save=save,
                    numvcpus=numvcpus,
                    memsize=memsize,
                    no_nat=no_nat)
                inst.created = True

            # Note: user/password is needed for provisioning
            vmrun = VMrun(inst.vmx, user=inst.user, password=inst.password)
            print(colored.blue("Bringing machine ({}) up...".format(instance)))
            started = vmrun.start(gui=gui)
            if started is None:
                print(colored.red("VM not started"))
            else:
                print(colored.blue("Getting IP address..."))
                lookup = inst.enable_ip_lookup
                ip_address = vmrun.get_guest_ip_address(lookup=lookup)
                if not disable_shared_folders:
                    utils.share_folders(vmrun, inst)
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

                # if not already using preshared key, switch to it
                if not inst.use_psk and inst.auth:
                    utils.add_auth(inst)
                    inst.switch_to_psk()

                if remove_vagrant:
                    utils.del_user(inst, 'vagrant')

                if not disable_provisioning:
                    utils.provision(inst, show=False)

    # allows "mech start" to alias to "mech up"
    start = up

    def global_status(self, arguments):  # pylint: disable=no-self-use,unused-argument
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
            # Note: user/password is needed for ps
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
                vmrun = VMrun(inst.vmx)

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
                    vmrun = VMrun(inst.vmx)
                    vmrun.stop(mode='hard', quiet=True)
                    vmrun.delete_vm()
                    if os.path.exists(inst.path):
                        shutil.rmtree(inst.path)
                    print("Deleted")
                else:
                    print(colored.red("Delete aborted."))
            else:
                print(colored.red("VM ({}) not created.".format(instance)))

    def down(self, arguments):
        """
        Stops the instances.

        Usage: mech down [options] [<instance>]

        Options:
            -f, --force                      Force a hard stop
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
                vmrun = VMrun(inst.vmx)
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
                vmrun = VMrun(inst.vmx)
                if vmrun.pause() is None:
                    print(colored.red("Not paused", vmrun))
                else:
                    print(colored.yellow("Paused", vmrun))
            else:
                print(colored.red("VM ({}) not created.".format(instance)))

    def upgrade(self, arguments):
        """
        Upgrade the vm file format and virtual hardware for the instance(s).

        Usage: mech upgrade [options] [<instance>]

        Note: The VMs must be created and stopped.

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
                vmrun = VMrun(inst.vmx)
                state = vmrun.check_tools_state(quiet=True)
                if state == "running":
                    print("VM must be stopped before doing upgrade.")
                else:
                    if vmrun.upgradevm(quiet=False) is None:
                        print(colored.red("Not upgraded", vmrun))
                    else:
                        print(colored.yellow("Upgraded", vmrun))
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

                vmrun = VMrun(inst.vmx)

                if vmrun.unpause(quiet=True) is not None:
                    print(colored.blue("Getting IP address..."))
                    lookup = inst.enable_ip_lookup
                    ip_address = vmrun.get_guest_ip_address(lookup=lookup)
                    if not disable_shared_folders:
                        utils.share_folders(vmrun, inst)
                    else:
                        print(colored.blue("Disabling shared folders..."))
                        vmrun.disable_shared_folders(quiet=False)
                    if ip_address:
                        print(colored.green("VM resumed on {}".format(ip_address)))
                    else:
                        print(colored.green("VM resumed on an unknown IP address"))

                else:
                    # Otherwise try starting
                    vmrun = VMrun(inst.vmx)
                    started = vmrun.start()
                    if started is None:
                        print(colored.red("VM not started"))
                    else:
                        print(colored.blue("Getting IP address..."))
                        lookup = inst.enable_ip_lookup
                        ip_address = vmrun.get_guest_ip_address(lookup=lookup)
                        if not disable_shared_folders:
                            utils.share_folders(vmrun, inst)
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
                print(colored.red("VM not created"))

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

            if inst.created:
                vmrun = VMrun(inst.vmx)
                if vmrun.suspend() is None:
                    print(colored.red("Not suspended", vmrun))
                else:
                    print(colored.green("Suspended", vmrun))
            else:
                print("VM has not been created.")

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

        Usage: mech ssh [options] <instance> [-- <extra-ssh-args>...]

        Options:
            -c, --command COMMAND            Execute an SSH command directly
            -p, --plain                      Plain mode, leaves authentication up to user
            -h, --help                       Print this help
        """
        plain = arguments['--plain']
        extra = arguments['<extra-ssh-args>']
        command = arguments['--command']

        instance = arguments['<instance>']

        inst = MechInstance(instance)

        if inst.created:
            rc, stdout, stderr = utils.ssh(inst, command, plain, extra)
            LOGGER.debug('command:%s rc:%d stdout:%s stderr:%s', command, rc, stdout, stderr)
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
            sys.exit(rc)
        else:
            print("VM not created.")

    def scp(self, arguments):  # pylint: disable=no-self-use
        """
        Copies files to and from the machine via SCP.

        Usage: mech scp [options] <src> <dst> [-- <extra-ssh-args>...]

        Options:
            -h, --help                       Print this help
        """
        extra = arguments['<extra-ssh-args>']
        src = arguments['<src>']
        dst = arguments['<dst>']

        dst_instance, dst_is_host, dst = dst.partition(':')
        src_instance, src_is_host, src = src.partition(':')

        instance_name = None
        if dst_is_host and src_is_host:
            sys.exit(colored.red("Both src and dst are host destinations"))
        if dst_is_host:
            instance_name = dst_instance
        else:
            dst = dst_instance
        if src_is_host:
            instance_name = src_instance
        else:
            src = src_instance

        if instance_name is None:
            sys.exit(colored.red("Could not determine instance name."))

        inst = MechInstance(instance_name)

        if inst.created:
            utils.scp(inst, src, dst, dst_is_host, extra)
        else:
            print(colored.red('VM not created.'))

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
            vmrun = VMrun(inst.vmx)
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
            -h, --help                       Print this help
            -s, --show-only                  Show the provisioning info (do not run)
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

            if inst.created:
                utils.provision(inst, show)
            else:
                print("VM not created.")

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

            if inst.created:
                vmrun = VMrun(inst.vmx)

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
            else:
                print("VM not created.")

    def port(self, arguments):
        """
        Displays information about guest port mappings.

        Usage: mech port [options] [<instance>]

        Options:
                --guest PORT                 Output the host port that maps to the given guest port
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
            vmrun = VMrun(inst.vmx)
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
                vmrun = VMrun(inst.vmx)
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
                # deal with box_version being none
                box_version = inst.box_version
                if inst.box_version is None:
                    box_version = ''
                print("{}\t{}\t{}\t{}".format(
                    colored.green(name.rjust(20)),
                    ip_address.rjust(15),
                    inst.box.rjust(35),
                    box_version.rjust(12)
                ))

    # allow 'mech ls' as alias to 'mech list'
    ls = list
