#!/usr/bin/env python
'''
mech.

Usage:
    mech init [<url>]
    mech (up | start) [options] [<name> --gui]
    mech (down | stop) [options] [<name>]
    mech suspend [options]
    mech pause [options]
    mech ssh [options] [--user=<user>]
    mech scp <src> <dst> [--user=<user>]
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
from clint.textui import prompt
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


def locate_vmx():
    vmx_files = glob.glob("*.vmx")
    if len(vmx_files) != 1:
        puts(colored.red("There are {} vmx files in the current directory. There must only be one.".format(
            len(vmx_files))))
        exit()
    return os.path.join(os.getcwd(), vmx_files[0])


def get_vm():
    mechfile = load_mechfile()
    vmx = mechfile.get('vmx')
    if vmx:
        vm = Vmrun(vmx)
        return vm
    puts(colored.red("Couldn't find a vmx"))
    exit()


def get_vm_user():
    mechfile = load_mechfile()
    user = mechfile.get('user')
    if user:
        return user
    else:
        return "mech"


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
    if mech_data == None:
        vmx = locate_vmx()

        decision = prompt.yn("It appears you do not have a mechfile, would you like to create one?")
        if decision:
            mech_data = {}
            mech_data["vmx"] = prompt.query("Vmx absolute path:", default=vmx)
            mech_data["url"] = "None"
            mech_data["user"] = "mech"

            save_mechfile(mech_data)
        else:
            puts(colored.red("Unable to load mechfile"))
            exit()
    return mech_data


def save_mechfile(config):
    puts("Saving {}".format(config.get('vmx')))

    mechfile = {
        'vmx':config.get('vmx'),
        'url':config.get('url'),
        'user':config.get('user')
    }
    json.dump(mechfile, open('mechfile', 'w+'), sort_keys=True, indent=4, separators=(',', ': '))
    puts(colored.green("Finished."))


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
    puts(colored.yellow("Checking box integrity..."))
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
    if url == None:
        puts(colored.green("Creating Mechfile from existing VM"))
        vmx = locate_vmx()
    elif url.startswith("http"):
        puts(colored.green("Downloading box from the internet"))
        vmx = setup_url(url)
    else:
        puts(colored.green("Installing box from local file"))
        vmx = setup_tar(url)
        url = None
    puts("Setting up {}".format(vmx))

    mechfile = {
        'vmx':vmx,
        'url':url,
        'user': "mech"
    }
    json.dump(mechfile, open('mechfile', 'w+'), sort_keys=True, indent=4, separators=(',', ': '))
    puts(colored.green("Finished."))


def mech_list():
    vms = glob.glob(os.path.join(HOME, '*'))
    for vm in vms:
        puts(os.path.basename(vm))


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
    puts(colored.yellow("Getting IP address..."))
    ip = vm.ip()
    puts(colored.green("VM started on {}".format(ip)))
    puts(colored.yellow("Sharing current folder..."))
    vm.enableSharedFolders()
    vm.addSharedFolder('mech', os.getcwd())
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


def mech_ssh(user):
    vm = get_vm()
    ip = vm.ip()
    if user == None:
        user = get_vm_user()
    if ip:
        puts("Connecting to {}".format(colored.green(ip)))
        os.system('ssh {}@{}'.format(user, ip))
    else:
        puts(colored.red("IP not found"))
        return

def mech_scp(user, src, dst):
    vm = get_vm()
    ip = vm.ip()
    if user == None:
        user = get_vm_user()
    if ip:
        src_is_host = src.startswith(":")
        dst_is_host = dst.startswith(":")

        if src_is_host and dst_is_host:
            puts(colored.red("Both src and host are host destinations"))
            exit()

        if dst_is_host:
            dst = dst[1:]
            puts("Sending {} to {}@{}:{}".format(
                src, colored.green(user), colored.green(ip), dst))
            os.system('scp {} {}@{}:{}'.format(src, user, ip, dst))
        else:
            src = src[1:]
            puts("Getting {} from {}@{}:{}".format(
                dst, colored.green(user), colored.green(ip), src))
            os.system('scp {}@{}:{} {}'.format(user, ip, src, dst))
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

    if not os.path.exists(HOME):
        os.makedirs(HOME)

    if arguments['init']:
        puts(colored.green("Initializing mech"))
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
        name = arguments.get("--user")
        mech_ssh(name)
        exit()

    elif arguments['scp']:
        name = arguments.get("--user")
        mech_scp(name, arguments['<src>'], arguments['<dst>'])
        exit()

    elif arguments['ip']:
        mech_ip()
        exit()

if __name__ == "__main__":
    main()
