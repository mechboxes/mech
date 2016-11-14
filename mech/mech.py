from vmrun import Vmrun
from clint.textui import colored, puts
import os
import glob
import utils

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
        else:
            vmx = utils.setup_tar(obj, name)

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

    def ip(self):
        vm = Vmrun(self.vmx)
        return vm.ip()