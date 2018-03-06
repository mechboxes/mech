from __future__ import print_function

import os
import sys
import glob
import time
import utils
import shutil

import requests
from clint.textui import colored, puts

from vmrun import VMrun


HOME = os.path.expanduser("~/.mech")

if not os.path.exists(HOME):
    os.makedirs(HOME)


class Mech(object):
    def get(self, name):
        if not hasattr(self, 'mechfile'):
            self.mechfile = utils.load_mechfile()
        return self.mechfile.get(name)

    @property
    def vmx(self):
        vmx = self.get('vmx')
        if vmx:
            return vmx
        puts(colored.red("Couldn't find a VMX in the mechfile"))
        sys.exit(1)

    @property
    def user(self):
        return self.get('user')

    ####################################################################

    def box_list(self):
        vms = glob.glob(os.path.join(HOME, 'boxes', '*'))
        for vm in vms:
            puts(os.path.basename(vm))

    def box_add(self, name, url, version=None):
        if url:
            if version:
                name = os.path.join(name, version)
            if any(url.startswith(s) for s in ('https://', 'http://', 'ftp://')):
                return utils.add_box_url(name, url)
            elif os.path.isfile(url):
                return utils.add_box_tar(name, url)
            else:
                return utils.add_box_url(name, 'https://' + url)

        elif name:
            account, _, box = name.partition('/')
            url = 'https://app.vagrantup.com/{account}/boxes/{box}'.format(account=account, box=box)
            try:
                data = requests.get(url).json()
                versions = data['versions']
                for v in versions:
                    current_version = v['version']
                    if not version or current_version == version:
                        for provider in v['providers']:
                            if 'vmware' in provider['name']:
                                url = provider['url']
                                print("Found url {} with provider {}".format(url, provider['name']))
                                name = os.path.join(name, current_version)
                                return utils.add_box_url(name, url)
                puts(colored.red("Couldn't find a VMWare compatible VM"))
            except requests.ConnectionError:
                puts(colored.red("Couldn't connect to Vagrant cloud API"))

    def init(self, name, url, version=None, force=False):
        if os.path.exists('mechfile') and not force:
            puts(colored.red("`mechfile` already exists in this directory."))
            puts(colored.red("Remove it before running `mech init`."))
            return

        puts(colored.green("Initializing mech"))
        box = self.box_add(name, url, version)
        if box:
            utils.init_box(box, url)
        puts(colored.red("Couldn't initialize mech"))

    def status(self):
        vm = VMrun()
        puts(vm.list())

    def start(self, gui=False):
        vm = VMrun(self.vmx)
        vm.start(gui=gui)
        time.sleep(3)
        if vm.installedTools():
            puts(colored.yellow("Getting IP address..."))
            ip = vm.getGuestIPAddress()
            puts(colored.green("VM started on {}".format(ip)))
            puts(colored.yellow("Sharing current folder..."))
            vm.enableSharedFolders()
            vm.addSharedFolder('mech', os.getcwd())
            puts(colored.green("VM started on {}".format(ip)))
        else:
            puts(colored.yellow("VMWare Tools is not installed or running..."))
            puts(colored.green("VM started"))

    def destroy(self, force=False):
        directory = os.path.dirname(self.vmx)
        name = os.path.basename(directory)
        if force or utils.confirm("Are you sure you want to delete {name} at {directory}".format(name=name, directory=directory), default='n'):
            puts(colored.green("Deleting..."))
            vm = VMrun(self.vmx)
            vm.stop(mode='hard')
            time.sleep(3)
            shutil.rmtree(directory)
        else:
            puts(colored.red("Deletion aborted"))

    def stop(self):
        vm = VMrun(self.vmx)
        if vm.installedTools():
            stopped = vm.stop()
        else:
            stopped = vm.stop(mode='hard')
        if stopped is None:
            puts(colored.red("Not stopped", vm))
        else:
            puts(colored.green("Stopped", vm))

    def pause(self):
        vm = VMrun(self.vmx)
        vm.pause()
        puts(colored.yellow("Paused", vm))

    def suspend(self):
        vm = VMrun(self.vmx)
        vm.suspend()
        puts(colored.green("Suspended", vm))

    def ssh(self, user=None):
        if user is None:
            user = self.user
        vm = VMrun(self.vmx)
        ip = vm.getGuestIPAddress()
        if ip:
            puts("Connecting to {}".format(colored.green(ip)))
            os.system('ssh {}@{}'.format(user, ip))
        else:
            puts(colored.red("IP not found"))

    def scp(self, src, dst, user=None):
        if user is None:
            user = self.user
        vm = VMrun(self.vmx)
        ip = vm.getGuestIPAddress()
        if ip:
            src_is_host = src.startswith(":")
            dst_is_host = dst.startswith(":")

            if src_is_host and dst_is_host:
                puts(colored.red("Both src and host are host destinations"))
                sys.exit(1)

            if dst_is_host:
                dst = dst[1:]
                puts("Sending {src} to {user}@{ip}:{dst}".format(
                    user=colored.green(user),
                    ip=colored.green(ip),
                    src=src,
                    dst=dst,
                ))
                os.system('scp {} {}@{}:{}'.format(src, user, ip, dst))
            else:
                src = src[1:]
                puts("Getting {user}@{ip}:{src} and saving in {dst}".format(
                    user=colored.green(user),
                    ip=colored.green(ip),
                    src=src,
                    dst=dst,
                ))
                os.system('scp {}@{}:{} {}'.format(user, ip, src, dst))
        else:
            puts(colored.red("IP not found"))

    def ip(self):
        vm = VMrun(self.vmx)
        ip = vm.getGuestIPAddress()
        if ip:
            puts(colored.green(ip))
        else:
            puts(colored.red("IP not found"))
