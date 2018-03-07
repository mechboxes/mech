from __future__ import print_function, division

import os
import sys
import glob
import json
import tarfile
import tempfile
import subprocess
import collections
from re import match, I
from shutil import copyfile

import requests

from clint.textui import colored, puts
from clint.textui import progress
from clint.textui import prompt


HOME = os.path.expanduser('~/.mech')


def locate_vmx(path):
    vmx_files = glob.glob(os.path.join(path, '*.vmx'))
    return vmx_files[0] if vmx_files else None


def parse_vmx(path):
    vmx = collections.OrderedDict()
    with open(path) as f:
        for line in f:
            line = line.strip().split('=', 1)
            vmx[line[0].rstrip()] = line[1].lstrip()
    return vmx


def rewrite_vmx(path):
    vmx = parse_vmx(path)

    # Check if there is an existing interface
    for vmx_key in vmx:
        if vmx_key.startswith('ethernet'):
            break
    else:
        # Write one if there is not
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
            row = "{} = {}".format(key, value)
            new_vmx.write(row + os.linesep)
    return True


def load_mechfile():
    pwd = os.getcwd()
    while pwd:
        mechfile = os.path.join(pwd, 'mechfile')
        if os.path.isfile(mechfile):
            with open(mechfile) as f:
                return json.load(f)
        pwd = os.path.basename(pwd)
    puts(colored.red("Couldn't find a mechfile in the current directory any deeper directories"))
    puts(colored.red("You can specify the name of the VM you'd like to start with mech up <name>"))
    puts(colored.red("Or run mech init to setup a tarball of your VM or download the VM"))
    sys.exit(1)


def add_box_url(name, url):
    boxname = os.path.basename(url)
    box = os.path.join(HOME, 'boxes', name, boxname)
    if not os.path.exists(box):
        try:
            r = requests.get(url, stream=True)
            length = int(r.headers['content-length'])
            with tempfile.NamedTemporaryFile() as f:
                for chunk in progress.bar(r.iter_content(chunk_size=1024), label=boxname, expected_size=(length // 1024) + 1):
                    if chunk:
                        f.write(chunk)
                f.flush()
                add_box_tar(name, f.name, url)
        except requests.ConnectionError:
            puts(colored.red("Couldn't connect to %s" % url))
            return
    return box


def add_box_tar(name, filename, url=None):
    puts(colored.blue("Checking box integrity..."))

    if os.name == 'posix':
        proc = subprocess.Popen(['tar', '-tqf' if sys.platform.startswith('darwin') else '-tf', filename, '*.vmx'])
        valid_tar = not proc.wait()
    else:
        tar = tarfile.open(filename, 'r')
        files = tar.getnames()
        valid_tar = False
        for i in files:
            if i.endswith('vmx'):
                valid_tar = True
                break
            if i.startswith('/') or i.startswith('..'):
                puts(colored.red("This box is comprised of filenames starting with '/' or '..'"))
                puts(colored.red("Exiting for the safety of your files"))
                sys.exit(1)

    if valid_tar:
        boxname = os.path.basename(url if url else filename)
        box = os.path.join(HOME, 'boxes', name, boxname)
        path = os.path.dirname(box)
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(box):
            copyfile(filename, box)
        return box


def init_box(filename, url):
    puts(colored.green("Extracting..."))
    if not os.path.exists('.mech'):
        os.makedirs('.mech')

        if os.name == 'posix':
            proc = subprocess.Popen(['tar', '-xf', filename], cwd='.mech')
            if proc.wait():
                puts(colored.red("Cannot extract box"))
                sys.exit(1)
        else:
            tar = tarfile.open(filename, 'r')
            tar.extractall('.mech')

    vmx = locate_vmx('.mech')
    save_mechfile({
        'box': filename,
        'vmx': vmx,
        'url': url,
        'user': prompt.query("What username would you like to save?", default='vagrant')
    }, '.')
    # rewrite_vmx(vmx)


def save_mechfile(mechfile, directory='.'):
    puts(colored.blue("Saving {}".format(os.path.join(directory, 'mechfile'))))
    with open(os.path.join(directory, 'mechfile'), 'w+') as f:
        json.dump(mechfile, f, sort_keys=True, indent=4, separators=(',', ': '))
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
