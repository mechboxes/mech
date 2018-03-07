# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017 Kevin Chung
# Copyright (c) 2018 German Mendez Bravo (Kronuz)
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

from __future__ import division

import os
import re
import sys
import glob
import json
import tarfile
import logging
import tempfile
import subprocess
import collections
from shutil import copyfile

import requests

from clint.textui import colored, puts
from clint.textui import progress
from clint.textui import prompt

logger = logging.getLogger(__name__)


HOME = os.path.expanduser('~/.mech')


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

        if re.match('y(?:es)?', input, re.IGNORE_CASE):
            return True

        elif re.match('n(?:o)?', input, re.IGNORE_CASE):
            return False


def save_mechfile(mechfile, directory='.'):
    puts(colored.blue("Saving {}".format(os.path.join(directory, 'mechfile'))))
    with open(os.path.join(directory, 'mechfile'), 'w+') as f:
        json.dump(mechfile, f, sort_keys=True, indent=4, separators=(',', ': '))
    puts(colored.green("Finished."))


def locate_vmx(path):
    vmx_files = glob.glob(os.path.join(path, '*.vmx'))
    return os.path.abspath(vmx_files[0]) if vmx_files else None


def parse_vmx(path):
    vmx = collections.OrderedDict()
    with open(path) as f:
        for line in f:
            line = line.strip().split('=', 1)
            vmx[line[0].rstrip()] = line[1].lstrip()
    return vmx


def update_vmx(path):
    vmx = parse_vmx(path)

    # Check if there is an existing interface
    for vmx_key in vmx:
        if vmx_key.startswith('ethernet'):
            return False

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
                try:
                    return json.load(f)
                except ValueError:
                    puts(colored.red("Invalid mechfile.\n"))
                    break
        pwd = os.path.basename(pwd)
    puts(colored.red("Couldn't find a mechfile in the current directory any deeper directories"))
    puts(colored.red("You can specify the name of the VM you'd like to start with mech up <name>"))
    puts(colored.red("Or run mech init to setup a tarball of your VM or download the VM"))
    sys.exit(1)


def add_box(descriptor, name=None, version=None, force=False, requests_kwargs={}):
    if name is None:
        name = os.path.splitext(os.path.basename(descriptor))[0]

    if any(descriptor.startswith(s) for s in ('https://', 'http://', 'ftp://')):
        if version:
            name = os.path.join(name, version)
        return add_box_url(name, descriptor, force=force, requests_kwargs=requests_kwargs)
    elif os.path.isfile(descriptor):
        try:
            with open(descriptor) as f:
                catalog = json.load(f)
        except Exception:
            if version:
                name = os.path.join(name, version)
            return add_box_tar(name, descriptor, force=force)
    else:
        account, _, box = descriptor.partition('/')
        url = 'https://app.vagrantup.com/{account}/boxes/{box}'.format(account=account, box=box)
        try:
            catalog = requests.get(url, **requests_kwargs).json()
        except requests.ConnectionError:
            puts(colored.red("Couldn't connect to HashiCorp's Vagrant Cloud API"))
            return

    versions = catalog.get('versions', [])
    for v in versions:
        current_version = v['version']
        if not version or current_version == version:
            for provider in v['providers']:
                if 'vmware' in provider['name']:
                    url = provider['url']
                    puts(colored.blue("Found url {} with provider {}".format(url, provider['name'])))
                    name = os.path.join(name, current_version)
                    return add_box_url(name, url, force=force, requests_kwargs=requests_kwargs)
    puts(colored.red("Couldn't find a VMWare compatible VM"))


def add_box_url(name, url, force=False, requests_kwargs={}):
    boxname = os.path.basename(url)
    box = os.path.join(HOME, 'boxes', name, boxname)
    if not os.path.exists(box) or force:
        try:
            r = requests.get(url, stream=True, **requests_kwargs)
            length = int(r.headers['content-length'])
            with tempfile.NamedTemporaryFile() as f:
                for chunk in progress.bar(r.iter_content(chunk_size=1024), label=boxname, expected_size=(length // 1024) + 1):
                    if chunk:
                        f.write(chunk)
                f.flush()
                add_box_tar(name, f.name, url=url, force=force)
        except requests.ConnectionError:
            puts(colored.red("Couldn't connect to %s" % url))
            return
    return box


def add_box_tar(name, filename, url=None, force=False):
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
        if not os.path.exists(box) or force:
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
    if not vmx:
        puts(colored.red("Cannot locate vmx"))
        sys.exit(1)

    if update_vmx(vmx):
        puts(colored.yellow("Added network interface to vmx"))

    save_mechfile({
        'box': filename,
        'vmx': vmx,
        'url': url,
        'user': prompt.query("What username would you like to save?", default='vagrant')
    }, '.')


def provision_file(vm, source, destination):
    return vm.copyFileFromHostToGuest(source, destination)


def provision_shell(vm, inline, path, args=[]):
    tmp_path = vm.createTempfileInGuest()
    if tmp_path is None:
        return

    try:
        if path and os.path.isfile(path):
            puts(colored.blue("Configuring script {}...".format(path)))
            if vm.copyFileFromHostToGuest(path, tmp_path) is None:
                return
        else:
            if path:
                if any(path.startswith(s) for s in ('https://', 'http://', 'ftp://')):
                    puts(colored.blue("Downloading {}...".format(path)))
                    try:
                        inline = requests.get(path).read()
                    except requests.ConnectionError:
                        return
                else:
                    puts(colored.red("Cannot open {}".format(path)))
                    return

            if not inline:
                puts(colored.red("No script to execute"))
                return

            puts(colored.blue("Configuring script..."))
            with tempfile.NamedTemporaryFile() as f:
                f.write(inline)
                f.flush()
                if vm.copyFileFromHostToGuest(f.name, tmp_path) is None:
                    return

        puts(colored.blue("Configuring environment..."))
        if vm.runScriptInGuest('/bin/sh', "chmod +x '{}'".format(tmp_path)) is None:
            return

        puts(colored.blue("Executing program..."))
        return vm.runProgramInGuest(tmp_path, args)

    finally:
        vm.deleteFileInGuest(tmp_path, quiet=True)
