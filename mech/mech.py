from vmrun import Vmrun
from clint.textui import colored, puts, prompt
import os
import glob
import utils
import requests
import shutil

HOME = os.path.expanduser("~/.mech")

if not os.path.exists(HOME):
    os.makedirs(HOME)

class Mech(object):
    """docstring for Mech"""
    def __init__(self):
        super(Mech, self).__init__()
        self.vmx = None
        self.url = None
        self.user = None
        self.gui = None


    @classmethod
    def setup(cls, obj, name):
        if obj.startswith("http"):
            vmx = utils.setup_url(obj, name)
        elif os.path.isfile(obj):
            vmx = utils.setup_tar(obj, name)
        else:
            account, box = obj.split('/')
            url = "https://app.vagrantup.com/{account}/boxes/{box}".format(account=account, box=box)
            data = requests.get(url).json()
            versions = data['versions']
            for v in versions:
                for provider in v['providers']:
                    if 'vmware' in provider['name']:
                        url = provider['url']
                        print "Found url {} with provider {}".format(url, provider['name'])
                        utils.setup_url(url, box)
                        return
            else:
                puts(colored.red("Couldn't find a VMWare compatible VM"))

    @classmethod
    def status(self):
        vm = Vmrun('')
        puts("".join(vm.list()))


    @classmethod
    def list(self):
        vms = glob.glob(os.path.join(HOME, '*'))
        for vm in vms:
            puts(os.path.basename(vm))


    def start(self):
        vm = Vmrun(self.vmx)
        if self.gui:
            vm.start(gui=True)
        else:
            vm.start()
        puts(colored.yellow("Getting IP address..."))
        ip = vm.ip()
        puts(colored.green("VM started on {}".format(ip)))
        puts(colored.yellow("Sharing current folder..."))
        vm.enableSharedFolders()
        vm.addSharedFolder('mech', os.getcwd())
        puts(colored.green("VM started on {}".format(ip)))


    def remove(self):
        directory = os.path.dirname(self.vmx)
        name = os.path.basename(directory)
        if utils.confirm("Are you sure you want to delete {name} at {directory}".format(name=name, directory=directory), default='n'):
            print "Deleting..."
            shutil.rmtree(directory)
        else:
            print "Deletion aborted"


    def stop(self):
        vm = Vmrun(self.vmx)
        vm.stop()
        puts(colored.green("Stopped", vm))


    def pause(self):
        vm = Vmrun(self.vmx)
        vm.pause()
        puts(colored.yellow("Paused", vm))


    def suspend(self):
        vm = Vmrun(self.vmx)
        vm.suspend()
        puts(colored.green("Suspended", vm))


    def ssh(self):
        vm = Vmrun(self.vmx)
        ip = vm.ip()
        if ip:
            puts("Connecting to {}".format(colored.green(ip)))
            os.system('ssh {}@{}'.format(self.user, ip))
        else:
            puts(colored.red("IP not found"))


    def scp(self, src, dst):
        vm = Vmrun(self.vmx)
        ip = vm.ip()
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
        vm = Vmrun(self.vmx)
        print self.vmx
        ip = vm.ip()
        puts(colored.green(ip))
        return ip