#!/usr/bin/env python
'''
mech.

Usage:
    mech (up | start) [options] [<name> --gui]
    mech (down | stop) [options] [<name>]
    mech pause [options]
    mech ssh [options] [--user=<user>]
    mech ip [options]
    mech (list | status) [options]
    mech -h | --help
    mech --version

Options:
    -h --help     Show this screen.
    --version     Show version.
    --debug       Show debug messages.
'''

from clint.textui import colored, puts
from clint.textui.progress import mill
from docopt import docopt
from vmrun import Vmrun
import glob
import os

def get_vmx():
    files = glob.glob('*.vmx')
    if files:
        return files[0]
    else:
        puts(colored.red("No vmx found. Please specify one with --name"))

def main(args=None):
    arguments = docopt(__doc__, version='mech 0.2.2')

    DEBUG = arguments['--debug']

    if arguments['list'] or arguments['status']:
        vm = Vmrun('')
        puts("".join(vm.list()))
        exit()

    vm = arguments['<name>'] if arguments['<name>'] else get_vmx()
    vm = Vmrun(vm, debug=DEBUG)

    if arguments['up'] or arguments['start']:
        puts(colored.yellow("Starting", vm))
        if arguments['--gui']:
            vm.start(gui=True)
        else:
            vm.start()
            ip = vm.ip()
            puts(colored.green("VM started on {}".format(ip)))

    if arguments['down'] or arguments['stop']:
        puts(colored.yellow("Stopping", vm))
        vm.stop()
        puts(colored.green("Stopped", vm))

    if arguments['pause']:
        puts(colored.yellow("Stopping", vm))
        vm.pause()

    if arguments['ssh']:
        ip = vm.ip()
        if ip:
            puts(colored.green(ip))
            user = arguments['--user'] if arguments['--user'] else "mech"
            os.system('ssh {}@{}'.format(user, ip))
        else:
            puts(colored.red("IP not found, could not SSH "))

    if arguments['ip']:
        ip = vm.ip()
        if ip:
            puts(ip)
        else:
            puts(colored.red("IP not found"))

if __name__ == "__main__":
    main()
