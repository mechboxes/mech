#!/usr/bin/env python
'''
mech.

Usage:
    mech init <url>
    mech (up | start) [options] [<name> --gui]
    mech (down | stop) [options] [<name>]
    mech suspend [options]
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
from clint.textui import progress
from docopt import docopt
from vmrun import Vmrun
from pprint import pprint
from fnmatch import fnmatch
import tarfile
import requests
import glob
import os
import json
import tempfile

HOME = os.path.expanduser("~/.mech")

def get_vm():
    mechfile = load_mechfile()
    vmx = mechfile.get('vmx')
    if vmx:
        vm = Vmrun(vmx)
        return vm
    puts(colored.red("Couldn't find a vmx"))
    exit()

def load_mechfile():
    pwd = os.getcwd()
    test_mechfile = os.path.join(pwd, "mechfile")
    mech_data = None
    if os.path.isfile(test_mechfile):
        with open(test_mechfile) as mechfile:
            mech_data = json.load(mechfile)
    else:
        for i in xrange(1 ,pwd.count(os.sep) + 1):
            amt = (os.pardir,) * i
            parent = os.path.join(*amt)
            end = os.path.join(pwd, parent, "mechfile")
            if os.path.isfile(end):
                with open(test_mechfile) as mechfile:
                    mech_data = json.load(mechfile)
                break
    return mech_data


def setup_url(url):
    r = requests.get(url, stream=True)
    filename = os.path.basename(url)
    path = os.path.join(HOME, 'tmp', filename)
    length = int(r.headers['content-length'])
    with tempfile.TemporaryFile() as f:
        for chunk in progress.bar(r.iter_content(chunk_size=1024), label=filename, expected_size=(length/1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()
        f.flush()
        f.seek(0)
        tar = tarfile.open(fileobj=f)
        files = tar.getnames()
        vmx = None
        for i in files:
            if i.endswith('vmx'):
                vmx = i
            if i.startswith('/') or i.startswith('..'):
                puts(colored.red("This box is comprised of filenames starting with '/' or '..'"))
                puts(colored.red("Exiting for the safety of your files"))
                exit()
        if vmx:
            puts(colored.green("Extracting..."))
            os.path.basename(vmx)
            folder, dot, ext = vmx.rpartition('.')
            path = os.path.join(HOME, folder)
            os.mkdir(os.path.join(HOME, folder), 0755)
            tar.extractall(path)
            return os.path.join(path, vmx)
    return os.path.abspath(path)


def setup_tar(filename):
    tar = tarfile.open(filename, 'r')
    files = tar.getnames()
    vmx = None
    for i in files:
        if i.endswith('vmx'):
            vmx = i
        if i.startswith('/') or i.startswith('..'):
            puts(colored.red("This box is comprised of filenames starting with '/' or '..'"))
            puts(colored.red("Exiting for the safety of your files"))
            exit()
    if vmx:
        puts(colored.green("Extracting..."))
        os.path.basename(vmx)
        folder, dot, ext = vmx.rpartition('.')
        path = os.path.join(HOME, folder)
        os.mkdir(os.path.join(HOME, folder), 0755)
        tar.extractall(path)
        return os.path.join(path, vmx)

def mech_init(url):
    if url.startswith("http"):
        vmx = setup_url(url)
    else:
        vmx = setup_tar(url)
        url = None
    print "Setting up", vmx

    mechfile = {
        'vmx':vmx,
        'url':url
    }
    json.dump(mechfile, open('mechfile', 'w+'), sort_keys=True, indent=4, separators=(',', ': '))
    puts(colored.green("Finished."))

def mech_list():
    vms = glob.glob(os.path.join(HOME, '*'))
    for vm in vms:
        print os.path.basename(vm)

def mech_status():
    vm = Vmrun('')
    puts("".join(vm.list()))

def mech_start(filename=False, gui=False):
    if filename:
        vm = Vmrun(filename)
    else:
        vm = get_vm()
    if gui:
        vm.start(gui=True)
    else:
        vm.start()
    ip = vm.ip()
    puts(colored.green("VM started on {}".format(ip)))

def mech_stop():
    vm = get_vm()
    vm.stop()
    puts(colored.green("Stopped", vm))

def mech_suspend():
    vm = get_vm()
    vm.suspend()
    puts(colored.green("Suspended", vm))

def mech_pause():
    vm = get_vm()
    puts(colored.yellow("Pausing", vm))
    vm.pause()

def mech_ssh(user="mech"):
    vm = get_vm()
    ip = vm.ip()
    if ip:
        puts(colored.green(ip))
        os.system('ssh {}@{}'.format(user, ip))
    else:
        puts(colored.red("IP not found"))
        return

def mech_ip():
    vm = get_vm()
    ip = vm.ip()
    if ip:
        puts(ip)
    else:
        puts(colored.red("IP not found"))


def main(args=None):
    arguments = docopt(__doc__, version='mech 0.3')

    DEBUG = arguments['--debug']

    if arguments['init'] and arguments['<url>']:
        mech_init(arguments['<url>'])
        exit()

    elif arguments['list']:
        mech_list()
        exit()

    elif arguments['status']:
        mech_status()
        exit()

    elif arguments['up'] or arguments['start']:
        start_args = (arguments['<name>'], arguments['--gui'])
        mech_start(*start_args)
        exit()

    elif arguments['down'] or arguments['stop']:
        mech_stop()
        exit()

    elif arguments['pause']:
        mech_pause()
        exit()

    elif arguments['suspend']:
        mech_suspend()
        exit()

    elif arguments['ssh']:
        name = arguments.get("--user", "mech")
        mech_ssh(name)
        exit()

    elif arguments['ip']:
        mech_ip()
        exit()

if __name__ == "__main__":
    main()
