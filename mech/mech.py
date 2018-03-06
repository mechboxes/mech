from __future__ import print_function

from vmrun import VMrun
from clint.textui import colored, puts
import os
import glob
import utils
import requests
import shutil

HOME = os.path.expanduser("~/.mech")

if not os.path.exists(HOME):
    os.makedirs(HOME)


class Mech(object):
    def __init__(self):
        self.vmx = None
        self.url = None
        self.user = None
        self.gui = None

    @classmethod
    def add(cls, name, url, version):
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

    @classmethod
    def init(cls, name, url, version, force):
        if os.path.exists('mechfile') and not force:
            puts(colored.red("`mechfile` already exists in this directory. Remove it before"))
            puts(colored.red("running `mech init`."))
            return

        box = cls.add(name, url, version)
        if not box:
            puts(colored.red("Couldn't initialize mech"))
            return

        utils.init_box(box, url)

    @classmethod
    def status(self):
        vm = VMrun('')
        puts(vm.list())

    @classmethod
    def list(self):
        vms = glob.glob(os.path.join(HOME, '*'))
        for vm in vms:
            puts(os.path.basename(vm))

    def start(self):
        vm = VMrun(self.vmx)
        vm.start(gui=self.gui)
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

    def destroy(self):
        directory = os.path.dirname(self.vmx)
        name = os.path.basename(directory)
        if self.force or utils.confirm("Are you sure you want to delete {name} at {directory}".format(name=name, directory=directory), default='n'):
            puts(colored.green("Deleting..."))
            shutil.rmtree(directory)
        else:
            puts(colored.red("Deletion aborted"))

    def stop(self):
        vm = VMrun(self.vmx)
        if vm.installedTools():
            vm.stop()
        else:
            vm.stop(mode='hard')
        puts(colored.green("Stopped", vm))

    def pause(self):
        vm = VMrun(self.vmx)
        vm.pause()
        puts(colored.yellow("Paused", vm))

    def suspend(self):
        vm = VMrun(self.vmx)
        vm.suspend()
        puts(colored.green("Suspended", vm))

    def ssh(self):
        vm = VMrun(self.vmx)
        ip = vm.getGuestIPAddress()
        if ip:
            puts("Connecting to {}".format(colored.green(ip)))
            os.system('ssh {}@{}'.format(self.user, ip))
        else:
            puts(colored.red("IP not found"))

    def scp(self, src, dst):
        vm = VMrun(self.vmx)
        ip = vm.getGuestIPAddress()
        user = self.user
        if ip:
            src_is_host = src.startswith(":")
            dst_is_host = dst.startswith(":")

            if src_is_host and dst_is_host:
                puts(colored.red("Both src and host are host destinations"))
                exit()

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
            return

    def ip(self):
        vm = VMrun(self.vmx)
        print(self.vmx)
        ip = vm.getGuestIPAddress()
        if ip:
            puts(colored.green(ip))
        else:
            puts(colored.red("IP not found"))
        return ip
