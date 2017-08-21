from clint.textui import colored, puts
from clint.textui import progress
from clint.textui import prompt
from docopt import docopt
from vmrun import Vmrun
from pprint import pprint
from fnmatch import fnmatch
from re import match, I
import tarfile
import requests
import glob
import os
import json
import tempfile
import collections


HOME = os.path.expanduser("~/.mech")

def locate_vmx(vm_name):
    path = os.path.join(HOME, vm_name, "*.vmx")
    vmx_files = glob.glob(path)
    if len(vmx_files):
        return vmx_files[0]
    else:
        return None


def parse_vmx(path):
    vmx = collections.OrderedDict()
    with open(path) as f:
        for line in f:
            line = line.strip().split('=', 1)
            vmx[line[0]] = line[1]
    return vmx


def rewrite_vmx(path):
    vmx = parse_vmx(path)
    vmx["ethernet0.addresstype"] = "generated"
    vmx["ethernet0.bsdname"] = "en0"
    vmx["ethernet0.connectiontype"] = "nat"
    vmx["ethernet0.displayname"] = "Ethernet"
    vmx["ethernet0.linkstatepropagation.enable"] = "FALSE"
    vmx["ethernet0.pcislotnumber"] = "32"
    vmx["ethernet0.present"] = "TRUE"
    vmx["ethernet0.virtualdev"] = "e1000"
    vmx["ethernet0.wakeonpcktrcv"] = "FALSE"
    with open(path, 'w') as new_vmx:
        for key in vmx:
            value = vmx[key]
            row = "{}={}".format(key, value)
            new_vmx.write(row + os.linesep)
    return True


def load_mechfile(name=None):
    if name:
        mechfile = os.path.join(HOME, name, 'mechfile')
        with open(mechfile) as data:
            mech_data = json.load(data)
        return mech_data
    else:
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


def setup_url(url, name):
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
            if not name:
                folder, dot, ext = vmx.rpartition('.')
                path = os.path.join(HOME, folder)
                os.mkdir(os.path.join(HOME, folder), 0755)
            else:
                path = os.path.join(HOME, name)
                os.mkdir(os.path.join(HOME, name), 0755)

            vmx_path = os.path.join(path, vmx)
            config = {
                'vmx':vmx_path,
                'url':url,
                'user': prompt.query("What username would you like to save?", default='mech')
            }
            tar.extractall(path)
            save_mechfile(config, path)
            save_mechfile(config, '.')
            rewrite_vmx(vmx_path)
            return os.path.join(path, vmx)
    return os.path.abspath(path)


def setup_tar(filename, name):
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
        if not name:
            folder, dot, ext = vmx.rpartition('.')
            path = os.path.join(HOME, folder)
            os.mkdir(os.path.join(HOME, folder), 0755)
        else:
            path = os.path.join(HOME, name)
            os.mkdir(os.path.join(HOME, name), 0755)
        tar.extractall(path)
        vmx_path = os.path.join(path, vmx)
        config = {
            'vmx': vmx_path,
            'url': None,
            'user': prompt.query("What username would you like to save?", default='mech')
        }
        save_mechfile(config, path)
        save_mechfile(config, '.')
        rewrite_vmx(vmx_path)
        return os.path.join(path, vmx)


def save_mechfile(config, directory='.'):
    puts("Saving {}".format(os.path.join(directory, 'mechfile')))

    mechfile = {
        'vmx':config.get('vmx'),
        'url':config.get('url'),
        'user':config.get('user')
    }
    json.dump(mechfile, open(os.path.join(directory, 'mechfile'), 'w+'), sort_keys=True, indent=4, separators=(',', ': '))
    puts(colored.green("Finished."))


def confirm(prompt, default='y'):
    default = default.lower()
    if default not in ['y', 'n']:
        default = 'y'
    choicebox = '[Y/n]' if default == 'y' else '[y/N]'
    prompt = prompt + ' ' + choicebox + ' '

    while True:
        input = raw_input(prompt).strip()
        if input == '':
            if default == 'y':
                return True
            else:
                return False

        if match('y(?:es)?', input, I):
            return True

        elif match('n(?:o)?', input, I):
            return False